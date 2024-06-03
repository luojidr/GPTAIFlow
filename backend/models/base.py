import json
import uuid
from datetime import date, datetime
from typing import List

from playhouse.shortcuts import model_to_dict
from playhouse.pool import PooledMySQLDatabase
from peewee import (
    Model,
    TextField,
    MySQLDatabase,
)

from peewee import *
from peewee import ModelSelect
from playhouse.shortcuts import ReconnectMixin
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT

from contrib.easy_compressor.flow_shortcut import get_decompress_flow_data_by_ids


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass


# 创建MySQL数据库连接
database = ReconnectMySQLDatabase('xxxx', user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOST, port=MYSQL_PORT)


def database_connection_context(function):
    def wrapper(*args, **kwargs):
        database.connect()
        result = function(*args, **kwargs)
        database.close()
        return result

    return wrapper

# database = SqliteDatabase("./data/my_database.db")


class JSONField(TextField):
    """Custom field to store JSON data as text in SQLite"""

    def db_value(self, value):
        if value is not None:
            return json.dumps(value)
        return None

    def python_value(self, value):
        if value is not None:
            return json.loads(value)
        return None


class BaseModel(Model):
    class Meta:
        database = database


def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return int(obj.timestamp() * 1000)
    elif isinstance(obj, uuid.UUID):
        return obj.hex
    raise TypeError(f"Type {type(obj)} not serializable")


def model_serializer(obj, many=False, manytomany=False):
    from models.workflow_models import WorkflowRunRecord

    results = []
    if many:
        for o in obj:
            dict_obj = model_to_dict(o, manytomany=manytomany)
            serialized_obj = json.dumps(dict_obj, default=json_serializer)
            results.append(json.loads(serialized_obj))
    else:
        dict_obj = model_to_dict(obj, manytomany=manytomany)
        serialized_obj = json.dumps(dict_obj, default=json_serializer)
        results.append(json.loads(serialized_obj))

    # 这里判断 obj 是 WorkflowRunRecord 对象，需要解压 data 属性数据
    is_run_records = isinstance(obj, WorkflowRunRecord) or \
                     (isinstance(obj, ModelSelect) and obj.model._meta.table_name == "workflowrunrecord")
    if not is_run_records:
        return results if many else results[0]

    # 优化查询
    data_ids: List[int] = [item["data_id"] for item in results if item.get("data_id")]
    general_details_ids: List[int] = [item["general_details_id"] for item in results if item.get("general_details_id")]

    # 解压数据
    decompress_data_dict = get_decompress_flow_data_by_ids(compressed_ids=data_ids + general_details_ids)

    for result in results:
        data_id = result["data_id"]
        general_details_id = result["general_details_id"]

        data_id and result.update(data=decompress_data_dict[data_id])
        general_details_id and result.update(general_details=decompress_data_dict[general_details_id])

    return results if many else results[0]
