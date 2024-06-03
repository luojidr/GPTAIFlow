# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-05-15 12:20:55
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-05-17 11:52:53
import uuid
import datetime

from peewee import (
    UUIDField,
    CharField,
    IntegerField,
    DateTimeField,
    ForeignKeyField,
    BigIntegerField,
    TextField,
    BooleanField,
    AutoField,
)

from models.base import BaseModel, JSONField
from models.user_models import User


class UserVectorDatabase(BaseModel):
    vid = UUIDField(default=uuid.uuid4, unique=True)
    user = ForeignKeyField(User, null=True, on_delete="SET NULL")
    STATUS_CHOICES = (
        ("INVALID", "无效"),
        ("EXPIRED", "已过期"),
        ("DELETING", "删除中"),
        ("DELETED", "已删除"),
        ("VALID", "有效"),
        ("ERROR", "错误"),
        ("CREATING", "创建中"),
    )
    status = CharField(choices=STATUS_CHOICES, default="CREATING")
    name = CharField()
    info = JSONField(default=dict)
    embedding_size = IntegerField(default=1536)
    embedding_model = CharField(default="text-embedding-ada-002")

    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)
    expire_time = DateTimeField(null=True)

    def __str__(self):
        return str(self.vid)

    class Meta:
        table_name = "user_vector_database"


class UserObject(BaseModel):
    oid = UUIDField(default=uuid.uuid4, unique=True)
    user = ForeignKeyField(User, null=True, on_delete="SET NULL")
    title = CharField()
    info = JSONField(default=dict)
    slug_url = CharField(null=True)
    TYPE_CHOICES = (
        ("TEXT", "文本"),
        ("IMAGE", "图片"),
        ("AUDIO", "音频"),
        ("VIDEO", "视频"),
        ("OTHER", "其他"),
    )
    data_type = CharField(choices=TYPE_CHOICES)
    STATUS_CHOICES = (
        ("IN", "无效"),
        ("PR", "处理中"),
        ("VA", "有效"),
    )
    status = CharField(choices=STATUS_CHOICES, default="VA")
    vector_database = ForeignKeyField(UserVectorDatabase, on_delete="CASCADE")
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)

    source_url = CharField(null=True)
    suffix = CharField(null=True)
    raw_data = JSONField(default=dict)
    embeddings = JSONField(default=list)

    def __str__(self):
        return str(self.oid)

    class Meta:
        table_name = "user_object"

class OpenAIHistory(BaseModel):
    
    chat_id = CharField(unique=True)
    user_id = UUIDField()
    input_tokens = BigIntegerField()
    output_tokens = BigIntegerField()
    input_str = TextField()    
    output_str = TextField()
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)
    model_type = CharField()
    rid = CharField()

    input_str_id = IntegerField(null=False, default=0)
    output_str_id = IntegerField(null=False, default=0)

    
class ClawerTables(BaseModel):
    uid = UUIDField(primary_key=True, default=uuid.uuid4)
    table_name = CharField(unique=True)
    value_infos = JSONField(default=dict)


class OpenAIAppUsage(BaseModel): 
    usage_id = UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = CharField()
    app_name = CharField()
    input_tokens = BigIntegerField()
    output_tokens = BigIntegerField()
    input_str = TextField()    
    output_str = TextField()
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)
    model_type = CharField()


class AIGCAppVersion(BaseModel):
    id = AutoField(primary_key=True)
    app_name = CharField()
    version = IntegerField()
    version_code = CharField()
    update_info = TextField()
    download_info = JSONField(default={})
    must_update = BooleanField(default=False)
    create_time = DateTimeField(default=datetime.datetime.now)


class AIGCAppJob(BaseModel):
    id = AutoField(primary_key=True)
    app_name = CharField()
    start_at = DateTimeField()
    end_at = DateTimeField()
    user_id = CharField()
    result = JSONField(default={})
    status = CharField()
    job_type = CharField()