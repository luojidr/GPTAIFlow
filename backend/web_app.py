# -*- coding: utf-8 -*-
import os
from peewee_migrate import Router
from playhouse.db_url import connect
import json
import queue
import threading
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, abort
import mimetypes
from flask_cors import CORS
import time
import traceback
import requests
from flask_jwt_extended import current_user
from const import TPYE_WEB_SERVER, TPYE_NODE_WORKER
import config

from api import API
from api.workflow_api import (
    WorkflowAPI,
    WorkflowTagAPI,
    WorkflowTemplateAPI,
    WorkflowRunRecordAPI,
    WorkflowRunScheduleAPI,
)
from api.database_api import DatabaseAPI, DatabaseObjectAPI
from api.user_api import SettingAPI,UserInfoAPI
from api.remote_api import OfficialSiteAPI
from api.openai_usage import TokenUsageAPI
from api.aigc_app import AIGCAppVersionAPI

from utilities.redis_utils import redis_conn
from utilities.web_crawler import proxies_for_requests
from models import create_tables
from models.base import database
from worker import clear_monitor_message, main_worker
from utilities.print_utils import logger
from contrib.easy_compressor.database import init_db_extension

# Some mimetypes are not correctly registered in Windows. Register them manually.
mimetypes.add_type("application/javascript", ".js")

if not Path("./data").exists():
    Path("./data").mkdir()
    Path("./data/static").mkdir()
    Path("./data/static/images").mkdir()

# Create SQLite tables. Will ignore if tables already exist.
create_tables()
# lock = FileLock('lockfile')


if Path("./version.txt").exists():
    with open("./version.txt", "r") as f:
        VERSION = f.read()
else:
    VERSION = os.environ.get("VECTORVEIN_VERSION", "0.0.1")

DEBUG = os.environ.get("VECTORVEIN_DEBUG", "0") == "1"
logger.info(f"Debug: {DEBUG}")
logger.info(f"Version: {VERSION}")

task_queue = queue.Queue()
vdb_queues = {
    "request": queue.Queue(),
    "response": queue.Queue(),
}
api = API(DEBUG, VERSION, task_queue, vdb_queues)
api_class_list = [
    WorkflowAPI,
    WorkflowTagAPI,
    WorkflowTemplateAPI,
    WorkflowRunRecordAPI,
    WorkflowRunScheduleAPI,
    DatabaseAPI,
    DatabaseObjectAPI,
    SettingAPI,
    OfficialSiteAPI,
    UserInfoAPI,
    TokenUsageAPI,
    AIGCAppVersionAPI,
]
for api_class in api_class_list:
    api.add_apis(api_class)


_proxies_for_requests = proxies_for_requests()


if "http" in _proxies_for_requests:
    os.environ["http_proxy"] = _proxies_for_requests["http"]
if "https" in _proxies_for_requests:
    os.environ["https_proxy"] = _proxies_for_requests["https"]

app_type = os.environ.get("APP_TYPE",TPYE_NODE_WORKER)
if app_type != TPYE_WEB_SERVER:
    for i in range(config.WORKER_THREAD_NUM):
        worker_thread = threading.Thread(target=main_worker, args=(task_queue, vdb_queues, i), daemon=True)
        worker_thread.start()


if DEBUG:
    url = os.environ.get("VITE_LOCAL", "web/index.html")
else:
    url = "web/index.html"

app=Flask(__name__)
CORS(app)
init_db_extension(app)

session = requests.Session()
DATABASE_URL = f'mysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/huace_nlp'
with app.app_context():
    # 连接数据库
    database = connect(DATABASE_URL)

    # 创建迁移路由器
    router = Router(database=database, migrate_dir='models/migrations')

    # 运行未执行的迁移
    router.run() 


@app.route('/root', methods=['GET','POST'])
def index():
    try:
        logger.info(f'get a new request')
        database.connect()
        logger.info(f'database connect succ')
        res = {}
        data = request.get_data()
        q_dict = json.loads(data)

        func = getattr(api,q_dict['path'])
        parameter = q_dict['parameter'] 
        user_id = q_dict.get('user_id','dada8b28-f495-4a8a-8a6a-4fe36490e17d')
        # user_id = str(current_user.user_id)  # jwt 后续处理
        parameter['user_id'] = user_id
        start = time.time()
        # if worker_url and q_dict.get("path")=="workflow__run":
        #     response = session.post(url = worker_url,json=request.json)
        #     database.close() 
        #     logger.info(f'send an workflow run request')
        #     return response.text
        logger.info(f'get request user_id: {user_id } api:{q_dict.get("path")}')
        res = func(q_dict['parameter'])
        try:
            res['data']['title'] = res['data']['title'].replace('?','')
        except:
            pass
        logger.info(f'request end user_id {user_id } api:{q_dict.get("path")} cost {time.time()-start}')
    except Exception as e:
        logger.error(f'request error {str(e)}')
        logger.error(traceback.format_exc())
        logger.error("q_dict: %s", q_dict)
    database.close() 
    return res


@app.route("/upload", methods=["POST"])
def save_file():
    file_name = request.form.get('file_name')
    file = request.files.get('file')

    user_name = request.form.get('user_name','NONE')
    logger.debug(f'request info :user name {user_name } api: upload  file_name:{file_name}')
    os.makedirs(f'tmp_data/{user_name}/', exist_ok=True)
    file.save(f'tmp_data/{user_name}/{file_name}')
    return {'upload_status':True,'file_path':f'tmp_data/{user_name}/{file_name}'}


FILES_PATH = 'tmp_data/files/'
@app.route("/files/<filename>")
def get_file(filename):
    try:
        return send_from_directory(FILES_PATH, filename)
    except FileNotFoundError:
        abort(404)


@app.route('/kill_rid', methods=['POST'])
def killrid():
    data = request.get_data()
    q_dict = json.loads(data)
    rid = q_dict.get('rid')
    if isinstance(rid,list):
        for element in rid:
            redis_conn.rpush(config.KILL_REDIS_KEY, element)
            redis_conn.expire(config.KILL_REDIS_KEY, 3600)
    else:
        redis_conn.rpush(config.KILL_REDIS_KEY, rid)
        redis_conn.expire(config.KILL_REDIS_KEY, 3600)
    return jsonify({"status": "OK", "message": "KISS SUCC"}), 200


@app.route('/healthcheck', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Service is running"}), 200


def registry(flask_app):
    from contrib.registry import RegistryApps

    RegistryApps(flask_app).ready()
    logger.warning("RegistryApps is ok!")


registry(app)


if __name__ == "__main__":
    app.run(port=config.PORT, host="0.0.0.0", debug=True)
