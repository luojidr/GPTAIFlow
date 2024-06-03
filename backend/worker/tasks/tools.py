# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-04-26 20:58:33
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-08-26 01:37:21
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from config import SERVER_DOMAIN
from utilities.batch_post import post_bulk
from utilities.workflow import Workflow
from utilities.web_crawler import MysqlTool, proxies, headers
from worker.tasks import task
from utilities.print_utils import logger

def convert_parameter_value(value, parameter_type):
    if parameter_type == "str":
        return str(value)
    elif parameter_type == "int":
        return int(value)
    elif parameter_type == "float":
        return float(value)
    elif parameter_type == "bool":
        return bool(value)
    return value  # if none of the types match


@task
def programming_function(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    code = workflow.get_node_field_value(node_id, "code")
    language = workflow.get_node_field_value(node_id, "language")
    fields = workflow.get_node_fields(node_id)
    list_input = workflow.get_node_field_value(node_id, "list_input")
    if isinstance(list_input, str):
        list_input = True if list_input.lower() == "true" else False

    parameters_batch = []
    for field in fields:
        if field in ("code", "language", "output", "list_input"):
            continue
        parameter = workflow.get_node_field_value(node_id, field)
        parameter_type = workflow.get_node(node_id).get_field(field).get("type")
        if list_input:
            parameters_batch = parameters_batch or [dict() for _ in range(len(parameter))]
            for batch, parameter_value in zip(parameters_batch, parameter):
                batch[field] = convert_parameter_value(parameter_value, parameter_type)
        else:
            parameters_batch = parameters_batch or [dict()]
            parameters_batch[0][field] = convert_parameter_value(parameter, parameter_type)

    pattern = r"```.*?\n(.*?)\n```"
    code_block_search = re.search(pattern, code, re.DOTALL)

    if code_block_search:
        pure_code = code_block_search.group(1)
    else:
        pure_code = code

    results = []
    for parameters in parameters_batch:
        if language == "python":
            exec(pure_code, globals())
            result = main(**parameters)
        else:
            result = "Not implemented"
        results.append(result)

    if not list_input:
        results = results[0]
    workflow.update_node_field_value(node_id, "output", results)
    return workflow.data


@task
def image_search(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    search_text = workflow.get_node_field_value(node_id, "search_text")
    search_engine = workflow.get_node_field_value(node_id, "search_engine")
    count = workflow.get_node_field_value(node_id, "count")
    output_type = workflow.get_node_field_value(node_id, "output_type")

    results = []
    if search_engine == "bing":
        if isinstance(search_text, list):
            search_texts = search_text
        else:
            search_texts = [search_text]
        for text in search_texts:
            params = {
                "q": text,
                "first": "-",
                "count": 30,
                "cw": 1920,
                "ch": 929,
                "relp": 59,
                "tsc": "ImageHoverTitle",
                "datsrc": "I",
                "layout": "RowBased_Landscape",
                "mmasync": 1,
            }
            images = []
            response = requests.get(
                "https://cn.bing.com/images/async",
                params=params,
                headers=headers,
                proxies=proxies(),
            )
            soup = BeautifulSoup(response.text, "lxml")
            images_elements = soup.select(".imgpt>a")
            for image_element in images_elements[:count]:
                image_data = json.loads(image_element["m"])
                title = image_data["t"]
                url = image_data["murl"]
                if output_type == "text":
                    images.append(url)
                elif output_type == "markdown":
                    images.append(f"![{title}]({url})")
            results.append(images)
    elif search_engine == "pexels":
        pexels_api_key = workflow.setting.get("pexels_api_key")
        if isinstance(search_text, list):
            search_texts = search_text
        else:
            search_texts = [search_text]
        for text in search_texts:
            params = {
                "query": text,
                "per_page": 30,
            }
            images = []
            response = requests.get(
                "https://api.pexels.com/v1/search",
                params=params,
                headers={"Authorization": pexels_api_key},
                proxies=proxies(),
            )
            data = response.json()
            for image_data in data["photos"][:count]:
                title = image_data["photographer"]
                url = image_data["src"]["original"]
                photographer = image_data["photographer"]
                pexels_photo_url = image_data["url"]
                if output_type == "text":
                    images.append(f"{url}\nPexels {photographer}: {pexels_photo_url}")
                elif output_type == "markdown":
                    images.append(
                        f"![{title}]({url})\nPexels {photographer}: [{pexels_photo_url}]({pexels_photo_url})"
                    )
            results.append(images)

    output = results if isinstance(search_text, list) else results[0]
    workflow.update_node_field_value(node_id, "output", output)
    return workflow.data


@task
def loop_invoke(workflow_data: dict, node_id: str):
    """循环执行节点. 对选择的节点循环执行1-n次.
    暂时只支持文本输出."""
    workflow = Workflow(workflow_data)
    node_obj = workflow.get_node(node_id)
    loop_num = node_obj.get_field("loop_num") or {"value": 0, "show": False, "field_type": "int"}
    
    # 循环结果执行获取
    data_node_id = f"{node_id}-{loop_num.get('value', 0)}"
    outputs: list = node_obj.get_field("loop_output")
    output = workflow.get_node_field_value(data_node_id, "output")
    outputs["value"].append(output)

    # 判断循环是否终止
    loop_end = False
    end_exp_code = workflow.get_node_field_value(node_id, "loop_end_exp_code")
    try:
        if end_exp_code:
            exec(end_exp_code, globals())
            loop_end = main(text=output, loop_num=loop_num["value"]) # type: ignore
    except Exception as e:
        logger.error(f"Error in loop_invoke: {e}")
        loop_end = False
    
    # 数据更新
    loop_num["value"] += 1
    node_obj.update_field("loop_num", loop_num)
    node_obj.update_field("loop_output", outputs)
    workflow.update_node_field_value(node_id, "loop_end", loop_end)
    
    # 删除不再需要的数据存储节点
    saved_nodes = []
    for _node in workflow.data["nodes"]:
        is_loop_node = node_id and len(node_id) != 36
        loop_node_id = _node.get("id")
        if is_loop_node and loop_node_id.startswith(f"-{loop_num}"):
           continue
        
        saved_nodes.append(_node)
    
    workflow.data["nodes"] = saved_nodes
    return workflow.data

@task
def task_monitor(workflow_data: dict, node_id: str):

    workflow = Workflow(workflow_data)
    user_id = workflow_data['user_id']
    urls = workflow.get_node_field_value(node_id, "urls")
    filter = workflow.get_node_field_value(node_id, "filter")
    length = workflow.get_node_field_value(node_id, "task_num") or len(urls)
    length = int(length)
    number = 0
    output_list = []
    for url in urls:
        match = re.search(r"rid=([0-9a-fA-F]+)", url)
        rid = match.group(1)       
        data = {"rid": rid}
        res = post_bulk("workflow_run_record__get", data, user_id)
        data = res.json().get('data')
        if not data:
            continue
        else:
            if data.get('general_details'):
                output_tag = data.get('general_details').get("output_tag")
                match = re.search(r"(\d+\.\d+)", output_tag)
                if match:
                    number = match.group(1)
                for input in data.get('general_details').get("ui_design").get("inputFields"):
                    if input.get("display_name") == "小说名":
                        book_name = input.get("value")
                    elif input.get("display_name") == "作者":
                        author = input.get("value")
                    else:
                        pass
                if float(number) >= float(filter):
                    output_list.append({"小说名称":book_name, "作者":author, "评分": number, "book_url": url})
                length -= 1
                with MysqlTool() as db:
                    check_sql = 'SELECT COUNT(*),rid FROM book_hash WHERE book_name = %s AND author = %s AND ip = %s GROUP BY rid'
                    result = db.execute(check_sql, (book_name, author, SERVER_DOMAIN))
                    if result and result[0][0] > 0:
                        logger.info(f"{book_name}-{author}记录已存在")
                        if result[0][1] != rid:
                            sql = "UPDATE book_hash SET rid = %s WHERE book_name = %s AND author = %s AND ip = %s"
                            db.execute(sql, (rid, book_name, author, SERVER_DOMAIN), commit=True)
                    else:
                        sql = 'INSERT INTO book_hash (book_name, author, score, rid, ip) VALUES (%s,%s,%s,%s,%s)'
                        db.execute(sql, (book_name, author, number, rid, SERVER_DOMAIN), commit=True)
                        logger.info(f"{book_name}-{author} 写入[book_hash]表成功")
            else:
                continue
    logger.info(f"还剩{length}条子任务未跑完")
    workflow.update_node_field_value(node_id, "task_num", str(length))
    workflow.update_node_field_value(node_id, "output", output_list)
    return workflow.data



    


