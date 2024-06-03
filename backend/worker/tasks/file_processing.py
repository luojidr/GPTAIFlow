# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-04-26 20:58:33
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-05-16 19:02:28
from copy import deepcopy
import os
from typing import Union
from config import FRONTEND_URL
from utilities.batch_post import post_bulk
from utilities.workflow import Workflow
from utilities.files import get_files_contents
from worker.tasks import task
from utilities.print_utils import logger
from utilities.sheet_handle import sheets_parse
import traceback

@task
def file_loader(
    workflow_data: dict,
    node_id: str,
):
    final_text=""
    workflow = Workflow(workflow_data)
    files = workflow.get_node_field_value(node_id, "files")
    prompt = workflow.get_node_field_value(node_id, "prompt")
    if not files and not prompt:
        raise ValueError("输入不能为空")
    if files:
        results, file_type = get_files_contents(files)
        if file_type:
            workflow.update_node_field_value(node_id, "output", results)
        else:
            for result in results:
                final_text+=result+"\n"
            workflow.update_node_field_value(node_id, "output", final_text)
    else:
        workflow.update_node_field_value(node_id, "output", prompt)
    return workflow.data


@task
def excel_parse(
    workflow_data: dict,
    node_id: str):
    logger.info(f"开始处理批量任务，节点id为 {node_id}")
    workflow = Workflow(workflow_data)
    files = workflow.get_node_field_value(node_id, "files")
    title = workflow.get_node_field_value(node_id, "prompt")
    content_list = sheets_parse(files)
    logger.info(f"content_list：{content_list}")
    logger.info(f"已上传的文件列表{files}")
    os.remove(files[0])
    parent_wid = workflow.workflow_id
    wid_data_list = []
    input_info = {}
    node_id_list = []
    rid_list = []
    user_id = workflow_data['user_id']
    partent_rid = workflow_data['rid']
    wid = ''
    try:
        data = {"search_text": title, "sort_field": "update_time", "sort_order": "descend"}
        results = post_bulk(data=data, path="workflow__list", user_id=user_id)
        workflows =  results.json().get('data').get("workflows")
        if workflows:
           wid =  workflows[0].get('wid', "")
           logger.info(f"wid为：{wid}")
        if not workflows:
            t_data = {"client": "PC", "search_text": title}
            temp_res = post_bulk(data=t_data, path="workflow_template__list", user_id=user_id)
            if temp_res.json().get('data').get("total") == 0:
                raise ValueError("您所输入的模板名称不存在")
            data = temp_res.json().get('data').get("templates")[0]
            res = post_bulk(data=data, path="workflow__create", user_id=user_id)
            if res.json().get("status") == 200:
                logger.info("模板创建成功")
                wid = res.json().get("data").get("wid")
        setting_res = post_bulk(data={}, path="setting__get", user_id=user_id)
        setting_data = setting_res.json().get('data').get('data')
        data = {"wid": wid}
        res = post_bulk(data=data, path="workflow__get", user_id=user_id)
        wid_data = res.json().get('data', [])
    except Exception:
        logger.error(f"获取workflow.data数据失败，失败原因{traceback.format_exc()}")
        workflow.update_node_field_value(node_id, "output", [])
    else:
        input_fields_map = {}
        for input in wid_data['data']["ui"]['inputFields']:
            node_id_list.append(input['nodeId'])
            input_info[input['category']] = list(set(node_id_list))
            input_fields_map[input["display_name"]] = {
                "name": input['name'],
                "node_id": input['nodeId']
            }
        for content in content_list:
            rid = content.get("rid")
            if rid:
                rid_url = f'http://{FRONTEND_URL}/#/workflow/{wid}?rid={rid}'
                rid_list.append(rid_url)
                continue
            wid_data = deepcopy(wid_data)
            wid_data['data']['setting'] = setting_data
            for key in content:
                for node in wid_data['data']['nodes']:
                    if node['category'] in input_info and node['id'] in input_info[node['category']]:
                            if key in node['data']['template']:
                                node['data']['template'][key]['value'] = content[key]
                            else:
                                # 通过display_name匹配name
                                input_field = input_fields_map.get(key)
                                if input_field and input_field['name'] in node['data']['template']:          
                                    if node['id'] == input_field['node_id']:
                                        node['data']['template'][input_field['name']]['value'] = content[key]
            wid_data_list.append(wid_data)
        try:
            for data in wid_data_list:
                res = post_bulk(data=data, path="workflow__run", user_id=user_id)
                status_code = res.json().get('status', 404)
                rid = res.json().get('data').get('rid')
                msg = res.json().get('msg')
                if status_code == 200:
                    logger.info(f"批量任务 {partent_rid} 的子任务 {rid} 流程下发成功")
                    from models.workflow_models import WorkflowRunRecord
                    WorkflowRunRecord.update({WorkflowRunRecord.parent_wid: parent_wid}).where(WorkflowRunRecord.rid==rid).execute()
                    rid_url = f'http://{FRONTEND_URL}/#/workflow/{wid}?rid={rid}'
                    rid_list.append(rid_url)
                else:
                    logger.error(f"批量任务 {partent_rid} 的子任务 {rid} 下发失败，失败原因{msg}")
                    raise ValueError(f"批量任务 {partent_rid} 的子任务 {rid} 下发失败，失败原因 {e}")
        except Exception as e:
            logger.error(f"任务流程下发失败，失败原因{traceback.format_exc()}")
            raise ValueError(f"任务流程下发失败，失败原因 {e}")
    workflow.update_node_field_value(node_id, "output", rid_list)
    return workflow.data