from models.workflow_models import WorkflowRunRecord
from playhouse.migrate import *
from utilities.print_utils import logger


# 创建一个迁移器


def migrate(migrator, database, **kwargse):
    # 定义要进行的迁移操作
    migrator.add_fields(WorkflowRunRecord, parent_wid=CharField(null=True, default='', index=True)),
    logger.info(f"parent_wid列添加成功")
    
