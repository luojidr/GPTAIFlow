import json
from typing import List, Dict, Optional
from datetime import datetime

from models import WorkflowRunRecord
from utilities.print_utils import logger
from utilities.redis_utils import workflow_redis_conn
from utilities.tools import workflow_record_cleaner
from extension import kafka_producer
import traceback
import config
import re
from contrib.easy_compressor.flow_shortcut import compress_workflowrunrecord, decompress_flow_data

REDIS_WORKFLOW_DATA_PREFIX = "workflow_data"


class DAG:
    def __init__(self):
        self.nodes = set()
        self.edges = {}

    def add_node(self, node):
        self.nodes.add(node)
        if node not in self.edges:
            self.edges[node] = set()

    def add_edge(self, start, end):
        if start not in self.nodes:
            self.add_node(start)
        if end not in self.nodes:
            self.add_node(end)
        self.edges[start].add(end)

    def get_parents(self, node):
        parents = []
        for start, ends in self.edges.items():
            if node in ends:
                parents.append(start)
        return parents

    def get_children(self, node):
        return list(self.edges[node])

    def get_all_nodes(self):
        return list(self.nodes)

    def topological_sort(self):
        in_degree = {node: 0 for node in self.nodes}
        for start, ends in self.edges.items():
            for end in ends:
                in_degree[end] += 1

        queue = [node for node, degree in in_degree.items() if degree == 0]

        result = []
        while queue:
            node = queue.pop(0)
            result.append(node)
            for child in self.edges[node]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if len(result) != len(self.nodes):
            raise ValueError("The graph contains cycles")

        return result


class Node:
    def __init__(self, node_data: dict):
        self.__node_data = node_data
        self.field_map = {field: data for field, data in node_data["data"]["template"].items()}

    def get_field(self, field: str) -> dict:
        return self.field_map.get(field, {})

    def update_field(self, field: str, data: dict):
        self.field_map[field] = data
        self.__node_data["data"]["template"][field] = data

    def get_status(self) -> int:
        return self.__node_data["data"].get("status", 0)

    def update_status(self, status: int):
        self.__node_data["data"]["status"] = status

    def update_credits(self, credits: int):
        self.__node_data["data"]["credits"] = credits
    
    @property
    def id(self) -> str:
        return self.__node_data["id"]

    @property
    def data(self) -> dict:
        return self.__node_data

    @property
    def task_name(self) -> str:
        return self.__node_data["data"]["task_name"]

    @property
    def type(self) -> str:
        return self.__node_data["type"]

    @property
    def category(self) -> str:
        return self.__node_data["category"]

    def __repr__(self) -> str:
        return f"<Node {self.type} @{self.id}>"


class Workflow:
    def __init__(self, workflow_data: dict):
        self.workflow_data = workflow_data
        if "original_workflow_data" not in workflow_data:
            self.original_workflow_data = json.loads(json.dumps(workflow_data))
            self.workflow_data["original_workflow_data"] = self.original_workflow_data
        else:
            self.original_workflow_data = workflow_data["original_workflow_data"]
        self.related_workflows = workflow_data.get("related_workflows", {})
        self.edges = self.workflow_data["edges"]
        self.nodes, self.workflow_invoke_nodes = self.parse_nodes()
        self.dag = self.create_dag()
        self.workflow_id = workflow_data.get("wid")
        self.record_id = workflow_data.get("rid")
        self.is_redo = workflow_data.get("is_redo", False)

    def parse_nodes(self):
        # 在没有【工作流调用】节点的情况下，所有节点就是原始数据中的nodes
        nodes_list: list[dict] = self.workflow_data["nodes"]
        nodes: dict[str, Node] = {}
        workflow_invoke_nodes: dict[Node] = {}
        while len(nodes_list) > 0:
            node = nodes_list.pop(0)
            node_obj = Node(node)

            match node_obj.type:
                case "WorkflowInvoke":
                    # 对于【工作流调用】节点，需要将子工作流的节点和边添加到当前工作流中
                    nodes_list.extend(self.handle_workflow_invoke(node_obj))
                    workflow_invoke_nodes[node_obj.id] = node_obj
                case "WorkflowLoopInvoke":
                    # 对于 [工作流循环调用]节点, 需要将循环执行的节点添加到当前工作流中
                    nodes_list.extend(self.handle_workflow_loop_invoke(node_obj))
                    # workflow_invoke_nodes[node_obj.id] = node_obj
                case _:
                    nodes[node["id"]] = node_obj
        # 更新原始数据中的nodes
        self.workflow_data["nodes"] = [node.data for node in nodes.values()]
        return nodes, workflow_invoke_nodes

    def handle_workflow_invoke(self, node_obj: Node) -> List[Dict]:
        """
        对【工作流调用】节点进行处理，将被调用的子工作流的节点和边添加到当前工作流中

        Args:
            node_obj (Node): 【工作流调用】节点

        Returns:
            list[dict]: 子工作流的节点列表
        """
        related_subnodes = self.get_related_subnodes(node_obj)
        subworkflow_id = node_obj.get_field("workflow_id").get("value")
        subworkflow = self.related_workflows.get(subworkflow_id)
        return self.add_subnodes_and_subedges(subworkflow, related_subnodes, node_obj)

    def handle_workflow_loop_invoke(self, node_obj: Node) -> List[Dict]:
        """
        对【工作流循环调用】节点进行处理，将循环执行的节点添加到当前工作流中.
        循环实现原理: 
        构造虚拟节点，将子项目的节点复制多份，每份的ID为 `node_id-{loop_num}`.
        每次执行时，执行复制的节点 将输出写到循环节点中.
        
        循环节点ID `node_id` 
        循环次数 `loop_num`
        循环第n次时 单次输出结果保存在 ID为 f'{node_id}-{loop_num}'的节点中
        多次循环的全部输出结果在`node_id` 节点中
        Args:
            node_obj (Node): 【工作流循环调用】节点
        
        Returns:
            List[Dict]: 所有循环中子工作流的节点列表
        """
        loop_count = int(node_obj.get_field("loop_count").get("value", 1))
        subworkflow_id = node_obj.get_field("workflow_id").get("value")
        subworkflow_dict = self.related_workflows.get(subworkflow_id)
        subworkflow = Workflow(subworkflow_dict)
        
        updated_subnodes = []
        loop_node = node_obj
        copied_output_node_ids = []
        
        related_subnode_ids = self.get_related_subnodes(loop_node)
        subnodes = subworkflow.nodes
        subedges = subworkflow.edges
        # 循环节点字段更新
        for subnode in subworkflow_dict.get("nodes", []):
            self.add_subnode(subnode, related_subnode_ids, node_obj)

        # 复制多分虚拟节点
        for loop_num in range(loop_count):
            copied_subnodes: dict[str, Node] = {}
            copied_subedges: list[dict] = []
            copied_related_subnode_ids = []
            for subnode_id, subnode in subnodes.items():
                copied_subnode_id = f"{subnode_id}-{loop_num}"
                copied_subnode = copy.deepcopy(subnode)
                copied_subnode.data["id"] = copied_subnode_id
                copied_subnodes[copied_subnode_id] = copied_subnode
                if subnode_id in related_subnode_ids:
                    copied_related_subnode_ids.append(copied_subnode_id)
                
                if subnode.category == "outputs":
                    # LoopData数据循环保存节点 每次循环的output保存在LoopData中
                    copied_output_node = copy.deepcopy(node_obj)
                    copied_output_node_id = f"{node_obj.id}-{loop_num}"
                    copied_output_node.data["type"] = "LoopData"
                    copied_output_node.data["id"] = copied_output_node_id
                    copied_output_node.data["data"]["task_name"] = "control_flows.empty"
                    copied_subnodes[copied_output_node_id] = copied_output_node
                    
                    # 子项目的虚拟节点输出到LoopData节点
                    copied_subedges.append({
                        "source": copied_subnode_id,
                        "sourceHandle": "text",
                        "target": copied_output_node_id,
                        "targetHandle": "output",
                    })
                    copied_output_node_ids.append(copied_output_node_id)
                    
            for subedge in subedges:
                copied_subedge = copy.deepcopy(subedge)
                source = subedge["source"]
                target = subedge["target"]
                if target in copied_output_node_ids:
                    continue
                if source != loop_node.id:
                    source = f"{source}-{loop_num}"
                if target != loop_node.id:
                    target = f"{target}-{loop_num}"
                    
                copied_subedge["source"] = source
                copied_subedge["target"] = target
                copied_subedges.append(copied_subedge)
            
            for subnode_id, subnode in copied_subnodes.items():
                # 复制的虚拟节点标记为 loop_node. 
                # loop_node 为True的节点在执行时不会按顺序排列到代执行任务列表中
                updated_subnode = self.add_subnode(subnode.data, copied_related_subnode_ids , node_obj)
                updated_subnode["data"]["loop_node"] = True
                updated_subnodes.append(updated_subnode)
            self.edges.extend(copied_subedges)  

        # LoopInvoke 节点记录多次循环的输出结果 循环次数等信息
        node_obj.data["type"] = "LoopInvoke"
        updated_subnodes.append(node_obj.data)
        return updated_subnodes

    def get_related_subnodes(self, node_obj: Node) -> List[str]:
        """
        找出【工作流调用】节点的显示字段有哪些，并且找出字段对应的实际工作流节点 ID

        Args:
            node_obj (Node): 【工作流调用】节点

        Returns:
            list[str]: 关联的子工作流节点 ID 列表
        """
        related_subnodes = []
        for field, field_data in node_obj.field_map.items():
            if field in ("workflow_id",):
                continue
            related_subnode = field_data.get("node")
            if related_subnode is not None:
                related_subnodes.append(related_subnode)
        return related_subnodes

    def add_subnodes_and_subedges(
        self,
        subworkflow: dict,
        related_subnodes: List[str],
        node_obj: Node,
    ):
        updated_subnodes = []
        for subnode in subworkflow.get("nodes", []):
            updated_subnode = self.add_subnode(subnode, related_subnodes, node_obj)
            updated_subnodes.append(updated_subnode)

        self.edges.extend(subworkflow.get("edges", []))
        return updated_subnodes

    def add_subnode(
        self,
        subnode: dict,
        related_subnodes: List[str],
        node_obj: Node,
    ):
        subnode_obj = Node(subnode)
        # 如果是在【工作流调用】节点中显示的节点，不能直接将原始节点添加到当前工作流中
        # 需要将原始节点的字段的值更新为【工作流调用】节点显示的字段的值
        if subnode_obj.id in related_subnodes:
            self.update_subnode_fields(subnode_obj, node_obj)
        return subnode_obj.data

    def update_subnode_fields(self, subnode_obj: Node, node_obj: Node):
        """
        如果是在【工作流调用】节点中显示的节点，不能直接将原始节点添加到当前工作流中
        需要将原始节点的字段的值更新为【工作流调用】节点显示的字段的值

        Args:
            subnode_obj (Node): 【工作流调用】节点中显示的子工作流节点
            node_obj (Node): 【工作流调用】节点
        """
        for subnode_field, subnode_field_data in subnode_obj.field_map.items():
            if subnode_field in ("workflow_id",):
                continue
            if subnode_field not in node_obj.field_map:
                # 不在【工作流调用】节点中显示的字段，不需要更新
                continue
            subnode_field_data["value"] = node_obj.get_field(subnode_field)["value"]
            subnode_obj.update_field(subnode_field, subnode_field_data)

    def create_dag(self):
        dag = DAG()
        for edge in self.edges:
            edge = self.update_edge_nodes(edge)
            dag.add_edge(edge["source"], edge["target"])
        self.add_isolated_nodes_to_dag(dag)
        return dag

    def update_edge_nodes(self, edge: dict):
        source = edge["source"]
        target = edge["target"]
        if source in self.workflow_invoke_nodes:
            workflow_invoke_node = self.workflow_invoke_nodes[source]
            original_source_node_field = workflow_invoke_node.get_field(edge["sourceHandle"])
            original_output_field_key = original_source_node_field.get("output_field_key")
            source = self.get_original_node(source, edge["sourceHandle"])
            edge["source"] = source
            edge["sourceHandle"] = original_output_field_key
        if target in self.workflow_invoke_nodes:
            target = self.get_original_node(target, edge["targetHandle"])
            edge["target"] = target
        return edge

    def get_original_node(self, node: str, handle: str):
        return self.workflow_invoke_nodes[node].get_field(handle).get("node")

    def add_isolated_nodes_to_dag(self, dag):
        all_nodes = dag.get_all_nodes()
        for node_id in self.nodes:
            node = self.get_node(node_id)
            if node_id not in all_nodes and node.category not in ["triggers", "assistedNodes"]:
                dag.add_node(node_id)

    def get_sorted_task_order(self) -> list:
        nodes_order = self.dag.topological_sort()
        tasks = []
        for node_id in nodes_order:
            node = self.get_node(node_id)
            
            # 循环任务的预置节点不一定会执行 由子任务的循环次数决定执行顺序和是否执行
            if node.data["data"].get("loop_node", False):
                continue
            task_name = node.task_name
            tasks.append(
                {
                    "node_id": node_id,
                    "task_name": task_name,
                }
            )
        return tasks

    def get_field_actual_node(self, node: Node, field_data: dict):
        if node.type != "WorkflowInvoke":
            return node
        subworkflow_id = node.get_field("workflow_id").get("value")
        subworkflow = self.related_workflows.get(subworkflow_id)
        field_source_node_id = node.get_field(field_data.get("field_key")).get("node")
        for subnode in subworkflow.get("nodes", []):
            subnode_obj = Node(subnode)
            if subnode_obj.id == field_source_node_id:
                return self.get_field_actual_node(subnode_obj, field_data)

    def update_original_workflow_data(self):
        """
        当存在【工作流调用】节点时，我们是将子工作流的节点和边添加到当前工作流中的。
        但最终返回给用户时不需要展开的工作流节点和边，因此需要替换为原始的节点并更新节点数据。
        """
        updated_nodes = []
        for node_data in self.original_workflow_data["nodes"]:
            original_node = Node(node_data)
            used_node = self.get_node(original_node.id)
            if used_node is not None:
                updated_nodes.append(used_node.data)
                continue
            for field, field_data in original_node.field_map.items():
                if field in ("workflow_id",):
                    continue
                actual_node = self.get_field_actual_node(original_node, {"field_key": field, **field_data})
                actual_field_data = actual_node.get_field(field)
                if len(actual_field_data) == 0:
                    actual_field_data = actual_node.get_field(field_data.get("output_field_key"))
                field_data["value"] = actual_field_data.get("value")
                original_node.update_field(field, field_data)
            updated_nodes.append(original_node.data)

        self.workflow_data["nodes"] = updated_nodes
        self.workflow_data["edges"] = self.original_workflow_data["edges"]

    def clean_workflow_data(self):
        self.workflow_data.pop("original_workflow_data", None)
        self.workflow_data.pop("related_workflows", None)

    def get_node(self, node_id: str) -> Node:
        return self.nodes.get(node_id)

    def get_node_field_value(self, node_id: str, field: str, default: str = None):
        """
        如果节点有连接的边，则以边的另一端节点作为输入值，忽略节点自身的value。
        同时将获取到的值更新到节点的value中。
        If the node has a connected edge,
        the other end of the edge is used as the input value,
        ignoring the value of the node itself.
        """
        node = self.get_node(node_id)
        if node is None:
            return default
        source_node = source_handle = ""
        for edge in self.edges:
            source_node = self.get_node(edge["source"])
            if source_node.type in ("Empty", "ButtonTrigger"):
                continue
            if edge["target"] == node_id and edge["targetHandle"] == field:
                source_node = edge["source"]
                source_handle = edge["sourceHandle"]
                break
        else:
            return node.get_field(field).get("value", default)

        source_node = self.get_node(source_node)
        input_data = source_node.get_field(source_handle).get("value", default)
        self.update_node_field_value(node_id, field, input_data)
        return input_data

    def update_node_field_value(self, node_id: str, field: str, value):
        node = self.get_node(node_id)
        field_data = node.get_field(field)
        field_data.update({"value": value})
        node.update_field(field, field_data)

    def get_node_fields(self, node_id: str):
        node = self.get_node(node_id)
        return node.data["data"]["template"].keys()

    def report_workflow_status(self, status: int, error_task: str = "",error_detail: str=""):
        try:
            status = "FINISHED" if status == 200 else "FAILED"
            data_dict = {"data":self.workflow_data}
            workflow_record_cleaner(data_dict)
            data = data_dict["data"]
            data["error_task"] = error_task
            data["error_detail"] = error_detail
            ui_design = get_UIDesignFromWorkflow(data)
            general_details = {
                "error_detail": error_detail,
                "error_task": error_task,
                "ui_design": ui_design,
                "output_tag": get_output_tag(ui_design),
                "input_tag": get_input_tag(ui_design),
            }
            save_workflow_data(self.record_id, data)
            WorkflowRunRecord.update(
                status=status,
                # data=data,
                # general_details=general_details,
                end_time=datetime.now()
            ).where(WorkflowRunRecord.rid == self.record_id).execute()

            # 数据压缩
            wrc_obj = WorkflowRunRecord.get(WorkflowRunRecord.rid == self.record_id)
            compress_workflowrunrecord(wrc_obj=wrc_obj, data=data, general_details=general_details)

            return True
        except Exception as e:
            logger.error(f"report_workflow_status failed: {e} record id:{self.record_id}")
            try:
                WorkflowRunRecord.update(status="FAILED").where(WorkflowRunRecord.rid == self.record_id).execute()
            except:
                pass
            return False

    def set_workflow_running(self):
        try:
            workflow_obj = WorkflowRunRecord.get(WorkflowRunRecord.rid == self.record_id)
            workflow_obj.status = "RUNNING"
            workflow_obj.start_time = datetime.now()
            workflow_obj.save()
            return True
        except Exception as e:
            logger.error(f"update_workflow_status failed: {e} record id {self.record_id}" )
            return False

    def set_node_status(
        self,
        node_id: str,
        status: int,
    ):
        node = self.get_node(node_id)
        node.update_status(status)
        return True

    @property
    def data(self):
        return self.workflow_data

    @property
    def setting(self):
        return self.workflow_data["setting"]

import copy
import json


def get_index(lst, condition):
    for i, elem in enumerate(lst):
        if condition(elem):
            return i
    return -1


def has_show_fields(node):
    has_show = False
    for key in node['data']['template'].keys():
        if node['data']['template'][key].get('show',False):
            has_show = True
    return has_show


type_value_map = {"Text":"text","Audio":"show_player","Mindmap":"show_mind_map","Mermaid":"show_mermaid","Echarts":"show_echarts","Table":"show_table"}
nonFormItemsTypes = ["typography-paragraph"]


def get_UIDesignFromWorkflow(workflowData):
    # import pdb;pdb.set_trace()
    inputFields = workflowData.get('ui', {}).get('inputFields', [])
    unusedInputFields = copy.deepcopy(inputFields)
    outputNodes = workflowData.get('ui', {}).get('outputNodes', [])
    unusedOutputNodes = copy.deepcopy(outputNodes)
    triggerNodes = workflowData.get('ui', {}).get('triggerNodes', [])
    unusedTriggerNodes = copy.deepcopy(triggerNodes)
    workflowInvokeOutputNodes = []

    for node in workflowData.get('nodes', []):
        if node.get('category') == 'triggers':
            triggerNodes.append(node)
            nodeIndex = get_index(unusedTriggerNodes, lambda n: n.get('id') == node.get('id'))
            if nodeIndex != -1:
                del unusedTriggerNodes[nodeIndex]
        elif node.get('category') == 'outputs':
            if node['type'] in ['Text', 'Audio', 'Mindmap', 'Mermaid', 'Echarts', 'Table']:
                if not node['data']['template'].get(f'{type_value_map[node["type"]]}',{}).get('value',False):
                    continue
            # ... 像上面这样，对于其他的类型也做相应的处理 ...
            elif node.get('type') == 'WorkflowInvokeOutput':
                workflowInvokeOutputNodes.append(node)
                continue
            else:
                continue
            prevNodeIndex = get_index(outputNodes, lambda n: n.get('id') == node.get('id'))
            if prevNodeIndex != -1:
                outputNodes[prevNodeIndex] = node
                unusedNodeIndex = get_index(unusedOutputNodes, lambda n: n.get('id') == node.get('id'))
                if unusedNodeIndex != -1:
                    del unusedOutputNodes[unusedNodeIndex]
            else:
                outputNodes.append(node)
        else:
            if not node.get('data', {}).get('has_inputs') and has_show_fields(node):
                continue
            for field in node.get('data', {}).get('template', {}).keys():
                if node.get('data', {}).get('template', {}).get(field, {}).get('show'):
                    nodeField = copy.deepcopy(node.get('data', {}).get('template', {}).get(field))
                    nodeField['category'] = node.get('category')
                    nodeField['nodeId'] = node.get('id')
                    nodeField['fieldName'] = field
                    prevFieldIndex = get_index(inputFields, lambda n: n.get('nodeId') == node.get('id') and n.get('fieldName') == field)
                    if prevFieldIndex != -1:
                        inputFields[prevFieldIndex] = nodeField
                        unusedFieldIndex = get_index(unusedInputFields, lambda n: n.get('nodeId') == node.get('id') and n.get('fieldName') == field)
                        if unusedFieldIndex != -1:
                            del unusedInputFields[unusedFieldIndex]
                    else:
                        inputFields.append(nodeField)

    # 删除没有用到的inputFields
    unusedInputFields = [field for field in unusedInputFields if field.get('field_type') not in nonFormItemsTypes]
    for field in unusedInputFields:
        fieldIndex = get_index(inputFields, lambda n: n.get('nodeId') == field.get('nodeId') and n.get('fieldName') == field.get('fieldName'))
        if fieldIndex != -1:
            del inputFields[fieldIndex]
    # 删除没有用到的outputNodes
    unusedOutputNodes = [node for node in unusedOutputNodes if node.get('field_type') not in nonFormItemsTypes]
    for node in unusedOutputNodes:
        nodeIndex = get_index(outputNodes, lambda n: n.get('id') == node.get('id'))
        if nodeIndex != -1:
            del outputNodes[nodeIndex]
    # 删除没有用到的triggerNodes
    for node in unusedTriggerNodes:
        nodeIndex = get_index(triggerNodes, lambda n: n.get('id') == node.get('id'))
        if nodeIndex != -1:
            del triggerNodes[nodeIndex]

    return {
        'inputFields': inputFields,
        'outputNodes': outputNodes,
        'triggerNodes': triggerNodes,
        'workflowInvokeOutputNodes': workflowInvokeOutputNodes,
    }


def get_workflow_sorted_tasks(workflow_data: dict) -> dict:
    """获取工作流的执行信息.
    
    Args:
        workflow_data (dict): 工作流的数据

    Returns:
        dict: 工作流的执行信息
    """
    try:
        workflow = Workflow(workflow_data)
        sorted_tasks = workflow.get_sorted_task_order()
        sorted_tasks_with_node_id = []
        for task in sorted_tasks:
            module, function = task["task_name"].split(".")
            module_task = {"module": module, "function": function, "node_id": task["node_id"]}
            # 循环任务的执行顺序递归处理
            if function == "loop_invoke":
                workflow_id = workflow.get_node_field_value(task["node_id"], "workflow_id")
                loop_count = workflow.get_node_field_value(task["node_id"], "loop_count")
                subworkflow_dict = workflow.related_workflows.get(workflow_id)
                module_task["submodule"] = get_workflow_sorted_tasks(subworkflow_dict)
                module_task["submodule"]["sorted_tasks_with_node_id"].append({
                    "module": "tools",
                    "function": "loop_invoke",
                    "node_id": task["node_id"],
                })
                module_task["submodule"]["task_amount"] += 1
                if loop_count:
                    module_task["submodule"]["loop_left"] = loop_count
            sorted_tasks_with_node_id.append(module_task)
        data = {
            "sorted_tasks_with_node_id": sorted_tasks_with_node_id,
            "record_id": workflow.record_id,
            "next_task": 0,
            "task_amount": len(sorted_tasks),
        }

        return data

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"get workflow sorted data error: {e}")

        workflow.report_workflow_status(500, "get_sorted_tasks",f"{e}")


def send_worklow_runinfo_to_mq(workflow_data):
    try:
        workflow = Workflow(workflow_data)
        logger.info(f'workflow start running, rid: {workflow.record_id}')
        data = get_workflow_sorted_tasks(workflow_data)
        kafka_producer.send(config.KAFKA_DEFAULT_TOPIC,data)
        logger.warning("Kafka推入的消息： topic: %s, data: %s", config.KAFKA_DEFAULT_TOPIC,data)
        workflow.set_workflow_running()
        logger.info(f'workflow sended to kafka, rid: {workflow.record_id}')
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"workflow sending error: {e}")

        workflow.report_workflow_status(500, "sending_to_kafka",f"{e}")


def get_output_tag(ui_design):
    res = ""
    for i in range(len(ui_design['outputNodes']) ):
        try:
            # 循环节点不输出Tag
            node_id = ui_design['outputNodes'][i]["id"]
            is_loop_node = len(node_id) != 36
            if is_loop_node:
                continue
            test_res = ui_design['outputNodes'][i]['data']['template']['text']['value']
            # 循环多次评估结果的输出Tag
            pattern = r"评估结果\D*(\d+(\.\d+)?)"
            match = re.search(pattern, test_res)
            if match:
                # 首次评估
                first_result_pattern = r"首次评分\D*(\d+(\.\d+)?)"
                first_result_match = re.search(first_result_pattern, test_res)
                if first_result_match:
                    res += "首次评估:" + str(first_result_match.group(1)) + "\n"
                res += "复评均分:" + str(match.group(1)) + "\n"
                
                # 评估次数:
                run_time_pattern = r"评估次数\D*(\d+(\.\d+)?)"
                run_time_match = re.search(run_time_pattern, test_res)
                if run_time_match:
                    res += "复评次数:" + str(int(run_time_match.group(1)) - 1) + "\n"
                res = res.strip()
            else:
                # 评估结果
                pattern = r"总体评价\D*(\d+(\.\d+)?)"
                #pattern = r"【总体评价】：\s*-\s*.*。总评分：(\d+\.\d+)"
                match = re.search(pattern, test_res)
                res += "总体评价:" + str(match.group(1))
        except:
            pass
    return res    


def get_input_tag(ui_design):
    text_ls = []
    try:
        for k in ui_design['inputFields']:
            # 循环节点输入不作为输入Tag
            node_id =k.get("nodeId")
            is_loop_node = node_id and len(node_id) != 36
            if is_loop_node:
                continue
            if type(k.get('value')) == list:
                for i in k.get('value'):
                    path = i.split('/')[-1] + "\n"
                    text_ls.append(path)
            else:
                text_ls.append(str(k.get("value"))+"\n")
        return text_ls
    except:
        pass
    return ""


def get_workflow_data(rid: str) -> dict:
    data_key = f"{REDIS_WORKFLOW_DATA_PREFIX}:{rid}"
    try:
        result = workflow_redis_conn.get(data_key)
        return  json.loads(result) if result else {}
    except Exception as e:
        logger.error(f"获取工作流数据失败: 报错: {e}")
        raise e


def save_workflow_data(rid: str, data: dict):
    data_key = f"{REDIS_WORKFLOW_DATA_PREFIX}:{rid}"
    try:
        expire = 60 * 60 * 3
        json_data = json.dumps(data, ensure_ascii=False)
        workflow_redis_conn.setex(data_key, expire, json_data)
    except Exception as e:
        logger.error(f"保存工作流数据失败: 报错: {e}")
        raise e

