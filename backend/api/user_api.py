from models import (
    User,
    Setting,
    model_serializer,
)
from api.utils import get_user_object_general, WorkflowData
from utilities.tools import get_webcam_id_by_code
from utilities.redis_utils import workflow_redis_conn
import json

class UserInfoAPI:
    name = "user_info"

    def login(self,payload):
        user_name = payload.get("user_name")
        password = payload.get("password")
        code = payload.get("code","")
        state = payload.get("state", "")
        response = {"status": 200, "msg": "success", "data": {}}
        if code:
            try:
                webcam_id = get_webcam_id_by_code(code)
                if not webcam_id:
                    raise Exception(f"get webcam id failed, code:{code}")
                user, _ = User.get_or_create(webcam_id=webcam_id, defaults={"user_name":webcam_id})
                response['data'] = {'user_id':str(user.user_id),'role':user.role}
                # 扫描二维码登陆 记录state登陆状态
                if state and len(state) == 36:
                    save_user_login_info(state, response['data'])
            except Exception as e:
                print('login failed',e)
                response = {"status": 500, "msg": "failed", "data": {}}
        else:
            user = User.select().where(User.user_name ==user_name)
            try:
                if user.first().password == password:
                    response['data'] = {'user_id':str(user.first().user_id),'role':user.first().role}
                else:
                    raise
            except Exception as e:
                response = {"status": 500, "msg": "failed", "data": {}}
                # response['data'] = {'user_id':'-1'}
        return response

    def qrlogin(self, payload):
        state =  payload.get("state")
        if not state:
            response = {"status": 500, "msg": "failed", "data": {}}
            return response
        user_data = get_user_login_data(state)
        if not user_data:
            response = {"status": 500, "msg": "failed", "data": {}}
            return response
        response = {"status": 200, "msg": "success", "data": user_data}
        return response
        
    def create(self,payload):
        user_name = payload.get("user_name")
        password = payload.get("password")
        try:
            user = User.insert({User.user_name :user_name,User.password : password}).execute()
            response = {"status": 200, "msg": "success", "data": {}}
            return response
        except:
            response = {"status": 500, "msg": "failled", "data": {}}
            return response

class SettingAPI:
    name = "setting"

    def get(self, payload):
        setting = Setting.select()
        if setting.count() == 0:
            setting = Setting.create()
        else:
            setting = setting.order_by(Setting.create_time.desc()).first()
        setting = model_serializer(setting)
        response = {"status": 200, "msg": "success", "data": setting}
        return response

    def update(self, payload):
        setting_id = payload.get("id")
        setting = Setting.get_by_id(setting_id)
        setting.data = payload.get("data", {})
        setting.save()
        setting = model_serializer(setting)
        response = {"status": 200, "msg": "success", "data": setting}
        return response

    def list(self, payload):
        user_id = payload.get("user_id")
        settings = Setting.select().where(Setting.user_id == user_id).order_by("create_time")
        settings_list = model_serializer(settings, many=True)
        response = {"status": 200, "msg": "success", "data": settings_list}
        return response

def get_user_login_data(state: str) -> dict:
    data_key = f"ACCOUNTINFO:{state}"
    try:
        result = workflow_redis_conn.get(data_key)
        return json.loads(result) if result else {}
    except Exception as e:
        raise e


def save_user_login_info(state: str, data: dict):
    data_key = f"ACCOUNTINFO:{state}"
    try:
        expire = 60  * 10
        json_data = json.dumps(data, ensure_ascii=False)
        workflow_redis_conn.setex(data_key, expire, json_data)
    except Exception as e:
        raise e