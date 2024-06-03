from peewee import (
    UUIDField,
    CharField,
    IntegerField,
    DateTimeField,
    ForeignKeyField,
    BigIntegerField,
    TextField,
    AutoField,
    FloatField,
)
from models import ClawerTables
from models.base import BaseModel,database

value_type_map = {"char":CharField,"text":TextField,"int":IntegerField, "float":FloatField}
clawer_models = {}

def register_clawer_models():
    
    for clawer_info in ClawerTables.select():
        class ClawerModel(BaseModel):
            id = AutoField()
            def __str__(self):
                return self.id
            class Meta:
                table_name = clawer_info.table_name
        clawer_model = ClawerModel
        for value_name,value_info in clawer_info.value_infos.items():
            max_length = int(value_info.get("max_length",-1))
            if max_length>=0:
                clawer_model._meta.add_field(value_name, value_type_map[value_info["type"]](max_length=max_length,null=True))
            else:
                clawer_model._meta.add_field(value_name, value_type_map[value_info["type"]](null=True))
        clawer_models[clawer_info.table_name] = clawer_model
    database.create_tables([v for k,v in clawer_models.items()])
    return clawer_models
