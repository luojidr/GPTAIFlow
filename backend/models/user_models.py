# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-05-15 12:43:18
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-05-15 22:53:41
import uuid
from datetime import datetime

from peewee import (
    UUIDField,
    DateTimeField,
    ForeignKeyField,
    CharField,
    DecimalField,
    DoubleField,
)

from models.base import BaseModel, JSONField


class User(BaseModel):
    """用户"""

    user_name = CharField(unique=True)
    password = CharField()
    user_id = UUIDField(primary_key=True, default=uuid.uuid4)
    create_time = DateTimeField(default=datetime.now)
    update_time = DateTimeField(default=datetime.now)
    cost = DoubleField()
    webcam_id = CharField()
    ROLE_CHOICES = (
        ("ADMIN", "管理员"),
        ("USER", "普通用户"),
        ("ROOT", "根用户"),
        ("EDITOR", "编辑"),
        ("HIGH_PRIORITY", "高优先级用户"),
    )
    role = CharField(max_length=16, choices=ROLE_CHOICES, default="USER", null=True)

    def __str__(self):
        return self.user_id.hex


class Setting(BaseModel):
    """设置"""

    user = ForeignKeyField(User, backref="setting", null=True)
    data = JSONField(default=dict)
    create_time = DateTimeField(default=datetime.now)
    update_time = DateTimeField(default=datetime.now)
