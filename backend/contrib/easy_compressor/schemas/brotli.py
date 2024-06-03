import json
from functools import cached_property
from typing import Union, Dict, Any

import brotli

from .base import BaseCompressor
from ..core.utils import MyDict


class BrotliCompressor(BaseCompressor):
    """ Brotli is lossless compression algorith on Google
        https://github.com/google/brotli
    """
    SCHEMA = "brotli"

    def __init__(self, **params: MyDict):
        super().__init__(**params)

        self.mode = self.options.get('model', brotli.MODE_GENERIC)
        self.quality = self.options.get('quality', 11)
        self.lgwin = self.options.get('lgwin', 22)
        self.lgblock = self.options.get('lgblock', 0)

    @cached_property
    def library(self):
        return brotli

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
