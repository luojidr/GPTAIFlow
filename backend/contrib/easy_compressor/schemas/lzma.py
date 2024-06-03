import lzma
from functools import cached_property
from typing import Union, Dict, Any

from .base import BaseCompressor
from ..core.utils import MyDict


class LzmaCompressor(BaseCompressor):
    SCHEMA = "lzma"

    def __init__(self, **params: MyDict):
        super().__init__(**params)

        self.format = self.options.get('format', lzma.FORMAT_XZ)
        self.check = self.options.get('check', -1)
        self.preset = self.options.get('preset')
        self.filters = self.options.get('filters')

    @cached_property
    def library(self):
        return lzma

    def compress(self,
                 data: Union[str, bytes],
                 data_type: int,
                 table_name: str,
                 pk_value: str,
                 col_name: str,
                 **kwargs
                 ) -> MyDict:
        return self._compress(
            data,
            data_type=data_type,
            table_name=table_name,
            pk_value=pk_value,
            col_name=col_name,
            options=None,
            **kwargs
        )

    def decompress(self, data: Union[str, bytes]) -> str:
        return self._decompress(data)
