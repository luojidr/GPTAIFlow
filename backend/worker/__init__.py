# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-05-15 16:56:55
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-05-29 15:30:39
import queue
import inspect
import random
import traceback

from utilities.workflow import Workflow, get_workflow_data, save_workflow_data
from utilities.print_utils import logger
from worker.tasks import chain, on_finish
from worker.tasks import (
    llms,
    tools,
    output,
    triggers,
    vector_db,
    web_crawlers,
    control_flows,
    file_processing,
    text_processing,
    image_generation,
    databases,
    voice,
)
from utilities.print_utils import logger

from utilities.redis_utils import redis_conn, GlobalLockPool
from extension import kafka_producer, kafka_consumer_list
from models import WorkflowRunRecord, User
import config
import time

from contrib.easy_compressor.flow_shortcut import compress_workflowrunrecord, decompress_flow_data


task_functions = {}
task_modules = [
    llms,
    tools,
    output,
    triggers,
    vector_db,
    web_crawlers,
    control_flows,
    file_processing,
    text_processing,
    image_generation,
    databases,
    voice,
]
for module in task_modules:
    functions = {}
    module_name = module.__name__.split(".")[-1]
    for name, obj in inspect.getmembers(module):
        if (
            callable(obj)
            and not inspect.isclass(obj)
            and not inspect.ismethod(obj)
            and obj.__class__.__name__ == "Task"
        ):
            functions[name] = obj
    task_functions[module_name] = functions


def main_worker(task_queue: queue.Queue, vdb_queues: dict, thread_num: int):
    """
    Main worker. Run in a separate thread.

    Args:
        task_queue (queue.Queue): Workflow run task queue
        vdb_queue (queue.Queue): Vector database related request queue
    """
    from web_app import app as flask_app

    while True:
        app_context = flask_app.app_context()
        app_context.push()

        try:
            kafka_consumer = kafka_consumer_list[thread_num]
            data = kafka_consumer.poll(timeout_ms=5, max_records=1)
            if data:
                for key in data:
                    consumerrecord = data.get(key)[0]
                    if consumerrecord != None:
                        # 配置一条数据  一小时执行一次 修复防止出现 kafka 重发的问题，后续继续修复kafka rebalance
                        lock = GlobalLockPool(
                            redis_conn,
                            str(consumerrecord.value),
                            lock_num=0,
                            max_expire_time=60 * 60 * 7,
                        )
                        if not lock.acquire_unblock() and consumerrecord.topic != config.KAFKA_MONITOR_TOPIC:
                            logger.info(
                                f'{consumerrecord.value.get("record_id")} ,{lock.key} has exec in 7 hour, skiped.'
                            )
                            # commit(kafka_consumer)
                            continue
                        try:
                            message = {
                                "Topic": consumerrecord.topic,
                                "Partition": consumerrecord.partition,
                                "Offset": consumerrecord.offset,
                                "Key": consumerrecord.key,
                                "Value": consumerrecord.value,
                            }
                            record_id = consumerrecord.value.get("record_id")
                            if record_id in redis_conn.lrange(
                                config.KILL_REDIS_KEY, 0, -1
                            ):
                                commit(kafka_consumer)
                                workflow_obj = WorkflowRunRecord.get(
                                    WorkflowRunRecord.rid == record_id
                                )
                                workflow_obj.status = "FAILED"
                                # workflow_obj.data["error_detail"] = "killed"
                                # workflow_obj.data["error_task"] = "killed"
                                # workflow_obj.data["error_detail"] = "killed"
                                # workflow_obj.general_details["error_detail"] = "killed"
                                # workflow_obj.general_details["error_task"] = "killed"

                                # 数据解压
                                workflow_data = decompress_flow_data(compress_id=workflow_obj.data_id)
                                general_details = decompress_flow_data(compress_id=workflow_obj.general_details_id)
                                workflow_data["error_detail"] = "killed"
                                workflow_data["error_task"] = "killed"
                                workflow_data["error_detail"] = "killed"
                                general_details["error_detail"] = "killed"
                                general_details["error_task"] = "killed"

                                workflow_obj.save()
                                logger.info(f"kill rid:{record_id}")

                                # 数据压缩
                                compress_workflowrunrecord(wrc_obj=workflow_obj, data=workflow_data, general_details=general_details)
                                continue
                            logger.info(f"Received message: {message}")
                            workflow_data = None
                            for i in range(3):
                                try:
                                    process_kafka_msg(consumerrecord.value)
                                    break
                                except Exception as e:
                                    if i ==2:
                                        logger.error(traceback.format_exc())
                                        logger.error(f"main_worker error: {e}")

                                        try:
                                            logger.error(f"error_task: {e.task_name}")
                                        except:
                                            e.task_name = "main_worker"
                                        if not workflow_data:
                                            workflow_obj = WorkflowRunRecord.get(
                                                WorkflowRunRecord.rid == record_id
                                            )
                                            # workflow_data = workflow_obj.data
                                            # 数据解压
                                            workflow_data = decompress_flow_data(compress_id=workflow_obj.data_id)

                                        workflow_data['rid'] = record_id
                                        workflow = Workflow(workflow_data)
                                        for (
                                            module_name,
                                            functions,
                                        ) in task_functions.items():
                                            if e.task_name in functions:
                                                logger.error(f"error_module: {module_name}")
                                                break
                                        if not hasattr(e, "error_detail"):
                                            e.error_detail = f"{e}"

                                        workflow.report_workflow_status(
                                            500,
                                            f"{module_name}.{e.task_name}",
                                            e.error_detail,
                                        )
                        except Exception as e:
                            logger.error(str(e))
                        commit(kafka_consumer)
                time.sleep(3)

            # task_data = task_queue.get()
            # print("worker receive task")

            # try:
            #     data: dict = task_data.get("data")
            #     workflow = Workflow(data)
            #     logger.info(f'workflow start running, rid: {workflow.record_id}')
            #     sorted_tasks = workflow.get_sorted_task_order()
            #     func_list = []
            #     sorted_tasks_with_node_id = []
            #     for task in sorted_tasks:
            #         module, function = task["task_name"].split(".")
            #         if module == "vector_db":
            #             func_list.append(task_functions[module][function].s(task["node_id"], vdb_queues))
            #         else:
            #             func_list.append(task_functions[module][function].s(task["node_id"]))
            #         sorted_tasks_with_node_id.append({"module":module,"function":function,"node_id":task["node_id"]})
            #     workflow.set_workflow_running()
            #     data = {"sorted_tasks_with_node_id":sorted_tasks_with_node_id,"workflow_data":workflow.data,"next_task":0,"task_amount":len(sorted_tasks)}
            #     kafka_producer.send(config.KAFKA_DEFAULT_TOPIC,data)

            #     task_chain = chain(*func_list, on_finish.s())
            #     task_chain(workflow.data)
            #     logger.info(f'workflow end running, rid: {workflow.record_id}')
            # except Exception as e:
            #     logger.error(traceback.format_exc())
            #     logger.error(f"main_worker error: {e}")
            #     logger.error(f"error_task: {e.task_name}")
            #     for module_name, functions in task_functions.items():
            #         if e.task_name in functions:
            #             logger.error(f"error_module: {module_name}")
            #             break
            #     if not hasattr(e,'error_detail'):
            #         e.error_detail = f"{e}"

            #     workflow.report_workflow_status(500, f"{module_name}.{e.task_name}",e.error_detail)
            # task_queue.task_done()
        except Exception as e:
            logger.info(f"get error {str(e)}")
            pass
        finally:
            app_context.pop()


def commit(kafka_consumer):
    try:
        kafka_consumer.commit()
    except:
        pass


def main_vector_database(vdb_queues: dict):
    """
    Vector database worker. Run in a separate thread.
    Qdrant local version uses SQLite which does not support multi-threading.

    Args:
        vdb_queue (queue.Queue): Vector database related request queue
    """
    from utilities.qdrant_utils import (
        add_point,
        delete_point,
        search_point,
        create_collection,
        delete_collection,
    )

    qrant_utils_functions = {
        "add_point": add_point,
        "delete_point": delete_point,
        "search_point": search_point,
        "create_collection": create_collection,
        "delete_collection": delete_collection,
    }
    vdb_request_queue = vdb_queues["request"]
    vdb_response_queue = vdb_queues["response"]
    while True:
        request = vdb_request_queue.get()
        function_name: dict = request.get("function_name")
        parameters: dict = request.get("parameters")
        logger.info(f"vector_database receive request {function_name}")
        try:
            function = qrant_utils_functions[function_name]
            response = function(**parameters)
            if function_name == "search_point":
                vdb_response_queue.put(response)
        except Exception as e:
            logger.error(f"main_vector_database error: {e}")
        vdb_request_queue.task_done()


def process_kafka_msg(consumerrecord_value: dict):
    """从kafka消息中获取到一个工作流节点，执行节点任务

    Args:
        consumerrecord_value (dict): kafka消息中的value
        workflow_data (dict): 工作流数据
    """
    next_task = consumerrecord_value["next_task"]
    sorted_tasks_with_node_id = consumerrecord_value["sorted_tasks_with_node_id"]
    function_name = sorted_tasks_with_node_id[next_task]["function"]
    task_amount = consumerrecord_value["task_amount"]
    record_id = consumerrecord_value["record_id"]
    workflow_obj = WorkflowRunRecord.select(WorkflowRunRecord.user_id).where(WorkflowRunRecord.rid == record_id).first()
    user_obj = User.get(User.user_id == workflow_obj.user_id)
    user_role = user_obj.role
    workflow_data = get_workflow_data(record_id)
    workflow_data["rid"] = record_id
    for task_num in range(next_task, task_amount):
        module = sorted_tasks_with_node_id[task_num]["module"]
        function_name = sorted_tasks_with_node_id[task_num]["function"]
        if (
            task_num > next_task
            and function_name
            in config.KAFKA_UNIQ_TOPIC_FUNCTION + config.KAFKA_OPENAI_TOPIC_FUNCTION
        ):
            break
        if function_name == "loop_invoke":
            consumerrecord_value = process_loop_subtasks(
                consumerrecord_value, workflow_data
            )
            if not consumerrecord_value:
                return
            else:
                consumerrecord_value['next_task'] += 1
                next_task += 1
                continue
        elif function_name == "task_monitor":
            node_id = sorted_tasks_with_node_id[task_num]["node_id"]
            result = task_functions[module][function_name](workflow_data=workflow_data, node_id=node_id)
            workflow = Workflow(result)
            length = workflow.get_node_field_value(node_id, "task_num")
            if int(length) == 0:
                continue
            else:
                data = {
                    "sorted_tasks_with_node_id": sorted_tasks_with_node_id,
                    "record_id": record_id,
                    "next_task": task_num,
                    "task_amount": task_amount,
                }
                send_node_to_kafka(node_id, function_name, workflow_data, user_role, data)
                return
        node_id = sorted_tasks_with_node_id[task_num]["node_id"]
        result = task_functions[module][function_name](
            workflow_data=workflow_data, node_id=node_id
        )
        workflow_data = result
        save_workflow_data(record_id, result)
        consumerrecord_value['next_task'] += 1
    if task_num + 1 >= task_amount:
        on_finish(workflow_data)
        logger.info(f"workflow end running, rid: {record_id}")
    else:
        data = {
            "sorted_tasks_with_node_id": sorted_tasks_with_node_id,
            "record_id": record_id,
            "next_task": task_num,
            "task_amount": task_amount,
        }
        node_id = sorted_tasks_with_node_id[task_num]["node_id"]
        send_node_to_kafka(node_id, function_name, workflow_data, user_role, data)


def get_kafka_queue_by_role(user_role: str, input_prompt: str) -> str:
    """根据用户类型和上下文长度获取对于的kafka队列

    Args:
        user_role (str): 用户角色
        input_prompt (str): 输入提示次

    Returns:
        str: kafka队列名称
    """
    if user_role in ["ADMIN", "HIGH_PRIORITY"]:
        # admin和高优用户的消息随机分配到openai高优先级队列
        admin_ques = (
            config.KAFKA_OPENAI_TOPIC_FUNCTION[3],
            config.KAFKA_OPENAI_TOPIC_FUNCTION[1],
        )
        return random.choice(admin_ques)
    elif len(str(input_prompt)) > 80000:
        return config.KAFKA_OPENAI_TOPIC_FUNCTION[2]
    else:
        return config.KAFKA_OPENAI_TOPIC_FUNCTION[0]


def send_node_to_kafka(
    node_id: str, function_name: str, workflow_data: dict, user_role: str, data: dict
):
    """发送节点任务到kafka队列

    Args:
        node_id (str): 节点id
        function_name (str): 函数名称
        workflow_data (dict): 工作流数据
        user_role (str): 用户角色
        data (dict): kafka消息数据
    """
    if function_name == "open_ai":
        # 调用 open ai 区分优先级 目前三个队列  高权限账号队列，短文本队列，长文本队列（大于5万字）
        workflow = Workflow(workflow_data)
        record_id = workflow.record_id
        input_prompt = workflow.get_node_field_value(node_id, "prompt")
        prompt_len = len(str(input_prompt))
        kafka_que = get_kafka_queue_by_role(user_role, input_prompt)
        logger.info(
            f"rid {record_id} kafka send to {kafka_que} ,prompt length {prompt_len}"
        )
        kafka_producer.send(kafka_que, data)
        input_prompt = None
        workflow = None
    elif function_name == "task_monitor":
        kafka_producer.send(config.KAFKA_MONITOR_TOPIC, data)
    else:
        kafka_producer.send(function_name, data)


def process_loop_subtasks(
    consumerrecord_value: dict, workflow_data: dict
) -> dict | None:
    """处理循环子任务

    Args:
        consumerrecord_value (dict): kafka消息中的value
        workflow_data (dict): 工作流数据

    Returns:
        tuple[bool, dict]: 需要发送的消息数据
    """
    next_task = consumerrecord_value["next_task"]
    task_amount = consumerrecord_value["task_amount"]
    record_id = consumerrecord_value["record_id"]

    sorted_tasks_with_node_id = consumerrecord_value["sorted_tasks_with_node_id"]
    function_name = sorted_tasks_with_node_id[next_task]["function"]
    workflow_obj = WorkflowRunRecord.get(WorkflowRunRecord.rid == record_id)
    user_obj = User.get(User.user_id == workflow_obj.user_id)
    user_role = user_obj.role

    loop_module = sorted_tasks_with_node_id[next_task]["submodule"]
    submodule_tasks = loop_module["sorted_tasks_with_node_id"]
    submodule_next_task = loop_module["next_task"]
    submodule_task_amount = loop_module["task_amount"]

    # loop_node_id = sorted_tasks_with_node_id[next_task]['node_id']
    data = {
        "record_id": record_id,
        "next_task": next_task,
        "task_amount": task_amount,
        "sorted_tasks_with_node_id": sorted_tasks_with_node_id,
    }
    loop_left = int(loop_module.get("loop_left", 0))
    loop_num = loop_module.get("loop_num", 0)
    

    result: dict = {}
    for sub_module_task_num in range(submodule_next_task, submodule_task_amount):
        module = submodule_tasks[sub_module_task_num]["module"]
        function_name = submodule_tasks[sub_module_task_num]["function"]
        if (
            sub_module_task_num > submodule_next_task
            and function_name
            in config.KAFKA_UNIQ_TOPIC_FUNCTION + config.KAFKA_OPENAI_TOPIC_FUNCTION
        ):
            break
        node_id = submodule_tasks[sub_module_task_num]["node_id"]
        if sub_module_task_num + 1 != submodule_task_amount:
            node_id = f"{node_id}-{loop_num}"

        result = task_functions[module][function_name](
            workflow_data=workflow_data, node_id=node_id
        )
        save_workflow_data(record_id, result)
        data["sorted_tasks_with_node_id"][next_task]["submodule"][
            "next_task"
        ] = sub_module_task_num
        
    # 执行到本次循环结束
    if sub_module_task_num + 1 >= submodule_task_amount:
        # workflow = Workflow(result)
        # loop_node = workflow.get_node(loop_node_id)
        loop_left -= 1
        loop_num += 1
        loop_module["loop_left"] = loop_left
        loop_module["loop_num"] = loop_num
        workflow = Workflow(result)
        node_id = submodule_tasks[sub_module_task_num]["node_id"]
        loop_end = workflow.get_node_field_value(node_id, "loop_end")
        if loop_left <= 0 or loop_end:
            # 循环完全结束
            return data
        else:
            # 循环继续
            loop_module['next_task'] = 0
            send_node_to_kafka(node_id, "common", workflow_data, user_role, data)
            return None

    else:
        loop_module["next_task"] = sub_module_task_num
        node_id = submodule_tasks[sub_module_task_num]["node_id"]
        node_id = f"{node_id}-{loop_num}"
        send_node_to_kafka(node_id, function_name, workflow_data, user_role, data)
        return None

# 每次重启都消费完monitor内所有的消息，避免消息进入死循环
def clear_monitor_message(consumer, topic_names = ["monitor"]):
    for topic_name in topic_names:
        consumer.subscribe([topic_name])

        # 消费未消费的消息
        while True:
            # 获取消息
            messages = consumer.poll(timeout_ms=1000)  # 调整超时时间根据需要
            if not messages:
                logger.info(f"No more messages in topic '{topic_name}'.")
                break  # 如果没有更多消息则退出循环

            # 处理消息
            for tp, msgs in messages.items():
                for msg in msgs:
                    logger.info(f"Consumed message from {msg.topic}, partition {msg.partition}, offset {msg.offset}")

            # 手动提交offset
            consumer.commit()

    # 关闭消费者
    consumer.close()