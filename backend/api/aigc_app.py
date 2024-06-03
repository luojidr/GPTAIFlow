from httpx import request
from models import (
    AIGCAppVersion, AIGCAppJob
)

class AIGCAppVersionAPI:
    name = "aigc_app_versions"

    def create(self, payload):
        app_name = payload.get("app_name")
        version = payload.get("version")
        version_code = payload.get("version_code")
        update_info = payload.get("update_info")
        download_info = payload.get("download_info")
        must_update = payload.get("must_update")
        try:
            AIGCAppVersion.insert(
                {
                    AIGCAppVersion.app_name: app_name,
                    AIGCAppVersion.version: version,
                    AIGCAppVersion.version_code: version_code,
                    AIGCAppVersion.update_info: update_info,
                    AIGCAppVersion.download_info: download_info,
                    AIGCAppVersion.must_update: must_update,
                }
            ).execute()
            response = {"status": 200, "msg": "success", "data": {}}
            return response
        except Exception as e:
            print(e)
            response = {"status": 500, "msg": "failled", "data": {}}
            return response

    def list(self, payload):
        app_name = payload.get("app_name")
        versions = AIGCAppVersion.select().filter(AIGCAppVersion.app_name == app_name).order_by(AIGCAppVersion.version.desc())
        version_models = [{
            "version_code": version.version_code,
            "version": version.version,
            "update_info": version.update_info,
            "download_info": version.download_info,
            "must_update": version.must_update,
            "create_time": version.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        } for version in versions]
        return {"status": 200, "msg": "success", "data": version_models}
    
    def get_latest_version(self, payload):
        app_name = payload.get("app_name")
        version = AIGCAppVersion.select().filter(AIGCAppVersion.app_name == app_name).order_by(AIGCAppVersion.version.desc()).first()
        version_model = {
            "version_code": version.version_code,
            "version": version.version,
            "update_info": version.update_info,
            "download_info": version.download_info,
            "must_update": version.must_update,
            "create_time": version.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return {"status": 200, "msg": "success", "data": version_model}
    
    def report_app_job(self, payload):
        app_name = payload.get("app_name")
        start_at = payload.get("start_at")
        end_at = payload.get("end_at")
        user_id = payload.get("user_id")
        result = payload.get("result")
        status = payload.get("status")
        job_type = payload.get("job_type")
        try:
            AIGCAppJob.insert(
                {
                    AIGCAppJob.app_name: app_name,
                    AIGCAppJob.start_at: start_at,
                    AIGCAppJob.end_at: end_at,
                    AIGCAppJob.user_id: user_id,
                    AIGCAppJob.result: result,
                    AIGCAppJob.status: status,
                    AIGCAppJob.job_type: job_type,
                }
            ).execute()
            response = {"status": 200, "msg": "success", "data": {}}
            return response
        except Exception as e:
            response = {"status": 500, "msg": f"{e.__str__()}", "data": {}}
            return response