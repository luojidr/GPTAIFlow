import abc
import json
import logging
from typing import Union, Optional

from deepdiff import DeepDiff

from ..core import signals
from ..models.text_compression import TextCompressionModel
from ..core.constant import DataTypeEnum, InsertModeEnum
from ..core.utils import MyDict, get_md5, encode_bytes, encode_base64_str, decode_base64_bytes


class BaseCompressor(abc.ABC):
    SCHEMA = None
    BATCH_SIZE = 100
    CompressModel = TextCompressionModel

    def __init__(self, **params: MyDict):
        self.options = params.get("options", {})
        self._native_data = None

        self._batch_results = []
        self._batch_size = params.get("batch_size", self.BATCH_SIZE)

    @property
    @abc.abstractmethod
    def library(self):
        pass

    @property
    def native_data(self):
        if self._native_data is None:
            raise ValueError("property `native_data` cannot be empty.")

        return self._native_data

    @native_data.setter
    def native_data(self, value):
        self._native_data = value

    def insert_batch(self, sender=None, immediate: bool = False):
        current_size: int = len(self._batch_results)

        if immediate or current_size >= self._batch_size:
            logging.warning("insert_batch has triggered => sender: %s, immediate: %s", sender, immediate)

            self.CompressModel.insert_bulk_objects(self._batch_results)
            self._batch_results = []

    def _compress(self,
                  data: Union[str, bytes, dict],
                  data_type: Union[int, DataTypeEnum],
                  table_name: str,
                  pk_value: str,
                  col_name: str,
                  options: Optional[MyDict] = None,
                  **kwargs
                  ) -> MyDict:
        if isinstance(data, dict):
            data: str = json.dumps(data, sort_keys=True)

        insert_mode = kwargs.get("insert_mode", InsertModeEnum.IMMEDIATE.value)
        if insert_mode not in [
            InsertModeEnum.BATCH.value,
            InsertModeEnum.IMMEDIATE.value,
        ]:
            raise ValueError(f"Parameter 'immediate' (value:{insert_mode}) must be 'immediate' or 'batch'")

        data: bytes = encode_bytes(data)
        self.native_data = data
        options = options or {}

        if self._native_data is None:
            raise ValueError("compress string cannot be empty.")

        before_text = encode_base64_str(self.native_data)
        compressed_bytes = self.library.compress(self.native_data, **options)
        after_text = encode_base64_str(compressed_bytes)

        if self.SCHEMA is None:
            raise ValueError("`SCHEMA` is empty.")

        # Must check integrity
        self.check_integrity(text=after_text, data_type=data_type)

        q_kw = dict(tb_name=table_name, pk_val=pk_value, col_name=col_name)
        instance = self.CompressModel.get_unique_record(after_text=after_text, schema=self.SCHEMA, **q_kw)

        if instance is None:
            obj_kwargs = dict(
                before_size=len(before_text), after_text=after_text,
                schema=self.SCHEMA, options=json.dumps(options or self.options),
                **q_kw
            )

            if insert_mode == InsertModeEnum.IMMEDIATE.value:
                instance = self.CompressModel.create(**obj_kwargs)
            else:
                cleaned_kwargs = self.CompressModel.get_cleaned_data(**obj_kwargs)
                instance = self.CompressModel(**cleaned_kwargs)
                self._batch_results.append(instance)

                signals.batch_saved.send(self)

        return instance.to_dict()

    def _decompress(self, data: Union[str, bytes]) -> str:
        data_bytes = decode_base64_bytes(data)
        native_data = self.library.decompress(data_bytes).decode('utf-8')  # 解压缩

        return native_data

    def check_integrity(self, text: Union[str, dict], data_type: Union[int, DataTypeEnum]):
        """ Check data integrity before and after compression
        :param text: compressed string
        :param data_type: `text` data type
        """
        native_data = self._decompress(data=text)
        data_type: int = data_type.type if not isinstance(data_type, int) else data_type

        if data_type == DataTypeEnum.TEXT.type:
            # Compare the md5 values before and after the string compression
            after_base64 = encode_base64_str(native_data)
            before_base64 = encode_base64_str(self.native_data)

            if get_md5(after_base64) != get_md5(before_base64):
                raise ValueError("文本压缩前后不一致！")

        elif data_type == DataTypeEnum.DICT.type:
            # Compare whether the dictionary is the same before and after compression
            after_dict = json.loads(native_data)
            before_dict = json.loads(self.native_data)
            diff = DeepDiff(after_dict, before_dict, ignore_order=True)

            if diff:
                raise ValueError(f"字典压缩前后不一致, Diff: {diff}")
        else:
            raise ValueError(f"数据类型(data_type: {data_type})错误, 无法进行验证")

