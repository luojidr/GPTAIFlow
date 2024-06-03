import sys
import logging
import pkgutil
from functools import cached_property
from typing import Union, Optional

from .core import signals
from .core.utils import MyDict
from .core.constant import InsertModeEnum, DataTypeEnum
from .core.exceptions import ImproperlyConfigured, InvalidCompressorSchemaError
from ..utils.module_loading import import_string

__author__ = 'dingxutao'
VERSION = (3, 6)
DEFAULT_COMPRESSOR_ALIAS = "default"

if sys.version_info < VERSION:
    raise EnvironmentError("Python version must be greater than 3.6")


class BaseCompressorHandler:
    thread_critical = False
    settings_name = "EASY_COMPRESSORS"

    def __init__(self, settings=None):
        self._settings = settings

    @cached_property
    def settings(self):
        """ django/flask config, eg.
            EASY_COMPRESSORS = {
                “default”: {
                    "schema": "easy_compressor.schemas.zlib.ZlibCompressor",
                    "options": {
                        "level": 2,
                    }
                },
                ......
            }
        """
        settings = None
        module = pkgutil.find_loader("django") or pkgutil.find_loader("flask")

        if module is not None:
            match module.name:
                case "django":
                    from django.conf import settings
                case "flask":
                    from flask import current_app
                    settings = current_app.config
                case _:
                    pass

        self._settings = self.configure_settings(settings)
        return self._settings

    def configure_settings(self, settings):
        _settings = getattr(settings, self.settings_name, None)
        if _settings is None:
            # brotli: the compression ratio is higher
            _settings = {
                DEFAULT_COMPRESSOR_ALIAS: {"schema": "easy_compressor.schemas.brotli.BrotliCompressor"}
            }

        return _settings


class EasyCompressorHandler(BaseCompressorHandler):
    def __init__(self):
        super().__init__()
        self._compressor_caches = {}

    def get_compressor(self, compressor_schema_path, options=None):
        prefix = "contrib."
        try:
            compressor_cls = import_string(prefix + compressor_schema_path)
        except ImportError as e:
            raise InvalidCompressorSchemaError(
                "Could not find schema '%s': %s" % (compressor_schema_path, e)
            ) from e

        return compressor_cls(**options or {})

    def __getitem__(self, alias):
        try:
            return self._compressor_caches[alias]
        except KeyError:
            compressor_schemas = self.settings

            for alias, compressor_schema in compressor_schemas.items():
                compressor_schema_path = compressor_schema.pop("schema")
                params = dict(**compressor_schema)
                _compressor = self.get_compressor(compressor_schema_path, **params)
                self._compressor_caches[alias] = _compressor

                signals.batch_saved.connect(_compressor.insert_batch)
                logging.warning("Already register 'batch-saved' signal to %s", _compressor)

        if not self._compressor_caches:
            raise ImproperlyConfigured("Could not load compressor in settings")

        return self._compressor_caches[alias]

    def all(self):
        return self._compressor_caches.values()


compressors = EasyCompressorHandler()


class DefaultEasyCompressorProxy:
    def __getattr__(self, name):
        # print(compressors._compressed.caches)
        return getattr(compressors[DEFAULT_COMPRESSOR_ALIAS], name)

    def __setattr__(self, name, value):
        return setattr(compressors[DEFAULT_COMPRESSOR_ALIAS], name, value)

    def __contains__(self, key):
        return key in compressors[DEFAULT_COMPRESSOR_ALIAS]


compressor = DefaultEasyCompressorProxy()


def compress_shortcut(
    s: Union[str, bytes],
    data_type: int,
    table_name: str,
    pk_value: str,
    col_name: str,
    insert_mode: Optional[str] = InsertModeEnum.IMMEDIATE.value
) -> MyDict:
    return compressor.compress(
        s,
        data_type=data_type,
        table_name=table_name,
        pk_value=pk_value,
        col_name=col_name,
        insert_mode=insert_mode
    )


def decompress_shortcut(s: Union[str, bytes]) -> str:
    return compressor.decompress(s)

