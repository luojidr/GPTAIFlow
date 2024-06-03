import json
import random

from worker.tasks import task
from utilities.workflow import Workflow
from utilities.database_utils import clawer_models

from func_timeout import func_set_timeout
import time
@task
# @func_set_timeout(100)
def query_data(
    workflow_data: dict,
    node_id: str,
):
    # time.sleep(100)
    final_text=""
    field_alias = {"rank":"排名","series_name":"名称","release_date":"上映时间","popularity":"热度","time_spread":"时间范围","brief":"剧情介绍","creators":"主创公司","actors":"演职员","douban_rate":"豆瓣评分","douban_rate_count":"豆瓣评分人数","male_rate":"男性比例","female_rate":"女性比例","max_age_rate":"最多年龄段占比","secondary_age_rate":"第二年龄段占比"}
    workflow = Workflow(workflow_data)
    table_name = workflow.get_node_field_value(node_id, "table_name")
    query = workflow.get_node_field_value(node_id, "query")
    delimeter = workflow.get_node_field_value(node_id, "delimeter")
    exclude = workflow.get_node_field_value(node_id, "exclude")
    exclude_fields = exclude.split(",")+["id"]
    
    clawer_model = clawer_models[table_name]
    for field in clawer_model._meta.fields:
        if field not in exclude_fields:
            final_text += field_alias[field] + delimeter
    final_text = final_text[:-1]+"\n"
    if query:
        rows = clawer_model.raw(query)
    else:
        rows = clawer_model.select()
    for row in rows:
        for field in clawer_model._meta.fields:
            if field not in exclude_fields:
                final_text += str(row.__getattribute__(field)).replace('\n',"") + delimeter
        final_text = final_text[:-1]+"\n"
    
    workflow.update_node_field_value(node_id, "output", final_text)
    return workflow.data
