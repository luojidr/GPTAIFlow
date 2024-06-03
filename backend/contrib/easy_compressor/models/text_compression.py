import logging
from typing import Union, Optional

from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, Text, DECIMAL, Enum, DATETIME, DateTime, Index, UniqueConstraint

from .base import BaseModel, db
from ..core.utils import get_hash, get_md5
from ..core.constant import TableEnum, AlgorithmEnum


class TextCompressionModel(BaseModel):
    __bind_key__ = "compression"
    __tablename__ = "text_compression"

    id = db.Column(db.BigInteger, primary_key=True)
    before_size = db.Column(db.Integer, nullable=False, server_default="0")  # 压缩前的base6长度
    after_size = db.Column(db.Integer, nullable=False, server_default="0")  # 压缩后的base6长度
    after_text = db.Column(db.Text(), nullable=False, server_default="")  # 压缩后的字节转base64字符串
    ratio = db.Column(db.DECIMAL(precision=8, scale=4), nullable=False, server_default="0.0")  # 压缩比

    # 枚举名称(db: varchar)
    algo_type = db.Column(db.Enum(AlgorithmEnum), nullable=False, server_default=AlgorithmEnum.BROTLI.name)  # 压缩类型
    options = db.Column(db.String(1000), nullable=False, server_default="")  # 压缩算法额外参数

    # tb_abbr, pk_val  辅助字段, 定位到原表的某一行
    tb_abbr = db.Column(db.String(50), nullable=False, server_default="")   # 压缩前表名缩写
    pk_val = db.Column(db.String(100), nullable=False, server_default="")   # 压缩前表主键值
    col_name = db.Column(db.String(50), nullable=False, server_default="")  # 压缩的列名
    pk_hash = db.Column(db.BigInteger, nullable=False, server_default='0')
    sign_hash = db.Column(db.BigInteger, nullable=False, index=True, server_default='0')
    create_time = db.Column(db.DateTime, nullable=False, default=func.now(), server_default=func.now())

    # db.Index("idx_pk_val", "pk_val")

    @staticmethod
    def _get_hash(pk_val: str, tb_abbr: str, col_name: str, algo_type: str, text: Optional[str] = None) -> int:
        if text:
            text_md5 = get_md5(text)
            string = f"{pk_val}-{tb_abbr}-{col_name}-{algo_type}-{text_md5}"
        else:
            string = f"{pk_val}-{tb_abbr}-{col_name}-{algo_type}"

        return get_hash(string)

    @classmethod
    def get_cleaned_data(cls, **kwargs):
        schema = kwargs.pop("schema")
        tb_name = kwargs.pop("tb_name")

        values = dict(**kwargs)
        before_size = kwargs["before_size"]
        after_text = kwargs["after_text"]
        after_size = len(after_text)

        values["after_size"] = after_size
        values["algo_type"] = AlgorithmEnum.get_algo_type(schema)
        values["ratio"] = "%.2f" % ((1 - after_size / before_size) * 100) if before_size > 0 else '0'
        values["pk_val"] = str(kwargs["pk_val"])
        values["tb_abbr"] = TableEnum.get_table_abbr(tb_name)

        hash_kw = dict(
            tb_abbr=values["tb_abbr"], pk_val=values["pk_val"],
            col_name=values["col_name"], algo_type=values["algo_type"]
        )
        values["pk_hash"] = cls._get_hash(**hash_kw)
        values["sign_hash"] = cls._get_hash(text=after_text, **hash_kw)

        return values

    @classmethod
    def create(cls, **kwargs):
        cleaned_kwargs = cls.get_cleaned_data(**kwargs)
        instance = super().create(**cleaned_kwargs)
        return instance

    @classmethod
    def get_unique_record(cls, after_text: str, pk_val: str, tb_name: str, col_name: str, schema: str) -> Optional[db.Model]:
        pk_val = str(pk_val)
        tb_abbr = TableEnum.get_table_abbr(tb_name)

        algo_type = AlgorithmEnum.get_algo_type(schema)
        sign_hash = cls._get_hash(pk_val, tb_abbr, col_name, algo_type, text=after_text)

        # with_entities => [<class 'sqlalchemy.engine.row.Row'>, ...]
        # queryset = cls.query.with_entities(cls.tb_abbr, cls.pk_val, cls.col_name).filter_by(sign_hash=sign_hash).all()
        queryset = cls.query.filter_by(sign_hash=sign_hash).all()
        count = len(queryset)

        if count > 1:
            args = (count, tb_name, pk_val, col_name)
            logging.warning("Query Compression count: %s from tb_name: %s, pk_val: %s, col_name: %s", *args)

        for obj in queryset:
            # row_dict = row._asdict()
            if obj.pk_val == pk_val and obj.tb_abbr == tb_abbr and obj.col_name == col_name:
                return obj

