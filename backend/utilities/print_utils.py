import logging
import logging.handlers
from pathlib import Path
from datetime import datetime, timedelta
import os
from concurrent_log_handler import ConcurrentRotatingFileHandler


group_id = int(os.environ.get("GROUP_ID", 0))
log_dir = Path("./log")
log_dir.mkdir(exist_ok=True)
days = 7
  

def setup_logger(name="vector-vein", level=logging.DEBUG):
    """
    Args:
    - name: 日志记录器的名字。
    - log_path: 存储日志文件的目录。
    - level: 日志等级。
    """
    # 检查超过10M的日志文件并备份,并且删除七天前的日志文件
    now = datetime.now()
    for log_file_path in log_dir.glob("vector-vein_*.log*"):
        # 获取文件的最后修改时间
        mtime = datetime.fromtimestamp(log_file_path.stat().st_mtime)
        # 如果文件的最后修改时间早于当前时间减去指定的天数，则删除文件
        if now - mtime > timedelta(days=days):
            log_file_path.unlink()  # 删除文件
    dt_now_str = datetime.now().strftime("%Y-%m-%d")

    # 设置日志文件名
    base_log_filename = f"{log_dir}/{name}_{dt_now_str}_{group_id}.log"

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s [%(thread)d] %(levelname)s: %(message)s')
    handler = ConcurrentRotatingFileHandler(base_log_filename, maxBytes=10*1024*1024, backupCount=5)
    filelog_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(filelog_formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # 创建控制台日志Handler
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger


logger = setup_logger()


