import json
import logging
import traceback
from typing import Optional, List, Union, Dict, Any

from . import compress_shortcut, decompress_shortcut
from .core.constant import InsertModeEnum, DataTypeEnum

__all__ = [
    "compress_workflowrunrecord",
    "compress_openaihistory",
    "decompress_flow_data",
    "get_decompress_flow_data_by_ids"
]

logger = logging.getLogger("vector-vein")


def get_decompress_flow_data_by_ids(
    compressed_ids: List[int],
    date_type: List[int] = DataTypeEnum.DICT.type
) -> Dict[int, Any]:
    from .models.text_compression import TextCompressionModel as model_cls

    results = {}
    fields = ["id", "after_text"]
    queryset = model_cls.query_selected_fields(model_cls.id.in_(compressed_ids), fields=fields)

    for obj in queryset:
        if date_type == DataTypeEnum.TEXT.type:
            results[obj.id] = obj.after_text
        else:
            decompress_str = decompress_shortcut(obj.after_text)
            results[obj.id] = json.loads(decompress_str)

    return results


def decompress_flow_data(compress_id: int, date_type: List[int] = DataTypeEnum.DICT.type) -> Union[dict, str]:
    """ 解压流程图相关数据

    Parameters
    ----------
    compress_id: 压缩表主键 ID
    date_type: 压缩的数据类型， 1: string, 2: dict
    """
    from .models.text_compression import TextCompressionModel

    assert date_type in [DataTypeEnum.TEXT.type, DataTypeEnum.DICT.type], f"不存在该解压的数据类型(date_type: {date_type})"

    instance = TextCompressionModel.query.get(compress_id)
    decompress_str = decompress_shortcut(instance.after_text)

    return decompress_str if date_type == DataTypeEnum.TEXT.type else json.loads(decompress_str)


def compress_workflowrunrecord(wrc_obj, data: Optional[dict] = None, general_details: Optional[dict] = None):
    """ 压缩 workflowrunrecord 表 data 与 general_details 数据"""
    # wrc_obj: Peewee model object
    if not data and not general_details:
        return

    pk_value = wrc_obj.rid.hex
    kwargs = dict(
        data_type=DataTypeEnum.DICT.type,
        table_name="workflowrunrecord",
        pk_value=pk_value,
        insert_mode=InsertModeEnum.IMMEDIATE.value
    )

    if data:
        try:
            result = compress_shortcut(s=json.dumps(data), col_name="data", **kwargs)
            wrc_obj.data_id = result["id"]
        except Exception as e:
            logger.error("压缩 workflowrunrecord(rid: %s)的 data 数据错误", pk_value)
            logger.error(traceback.format_exc())
            wrc_obj.data = data

    if general_details:
        try:
            result = compress_shortcut(s=json.dumps(general_details), col_name="general_details", **kwargs)
            wrc_obj.general_details_id = result["id"]
        except Exception as e:
            logger.error("压缩 workflowrunrecord(rid: %s)的 general_details 数据错误", pk_value)
            logger.error(traceback.format_exc())
            wrc_obj.general_details = general_details

    # Peewee save
    wrc_obj.save()


def compress_openaihistory(oai_obj, input_str: Optional[str], output_str: Optional[str]):
    kwargs = dict(
        data_type=DataTypeEnum.TEXT.type,
        table_name="openaihistory",
        pk_value=str(oai_obj.id),
        insert_mode=InsertModeEnum.IMMEDIATE.value
    )

    if input_str:
        result = compress_shortcut(s=input_str, col_name="input_str", **kwargs)
        oai_obj.input_str_id = result["id"]

    if output_str:
        result = compress_shortcut(s=output_str, col_name="output_str", **kwargs)
        oai_obj.output_str_id = result["id"]

    # Peewee save
    oai_obj.save()
