import enum


class BaseEnum(enum.Enum):
    @classmethod
    def iterator(cls):
        return iter(cls._member_map_.values())


class AlgorithmEnum(BaseEnum):
    ZLIB = 1
    GZIP = 2
    BZ2 = 3
    LZMA = 4
    LZ4 = 5
    SNAPPY = 6
    ZSTD = 7
    BROTLI = 8

    @classmethod
    def get_algo_type(cls, schema):
        for e in cls.iterator():
            if schema.upper() == e.name:
                return e.name

        raise ValueError(f"`{schema}` is incorrect schema.")


class TableEnum(BaseEnum):
    WORKFLOW = ("WFW", "workflow")		                    # workflow
    OPENAI_HISTORY = ("OAI", "openaihistory")				# openaihistory
    WORKFLOW_RUN_RECORD = ("WRC", "workflowrunrecord")		# workflowrunrecord

    @property
    def abbr(self) -> str:
        return self.value[0]

    @property
    def tb_name(self) -> str:
        return self.value[1]

    @classmethod
    def get_table_abbr(cls, tb_name):
        for e in cls.iterator():
            if tb_name == e.tb_name:
                return e.abbr

        raise ValueError(f"`{tb_name}` is not exist.")


class DataTypeEnum(BaseEnum):
    TEXT = (1, "string")
    DICT = (2, "dictionary")

    @property
    def type(self) -> int:
        return self.value[0]

    @property
    def name(self) -> str:
        return self.value[1]


class InsertModeEnum(BaseEnum):
    BATCH = "batch"
    IMMEDIATE = "immediate"


