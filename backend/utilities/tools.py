from models import WorkflowTag, User
from const import TAG_COLORS_SET, WEBCAM_CORP_ID, WEBCAM_CORP_SECRET
import requests

session = requests.session()
corpid=WEBCAM_CORP_ID
corpsecret=WEBCAM_CORP_SECRET

# 将tag按标题绑定到工作流，并赋予不同颜色
def tag_register(workflow, tags):
    workflow.tags.clear()
    tag_color_count = {color:0 for color in TAG_COLORS_SET}
    tag_to_add = set()
    for tag in tags:
        tag_qs = WorkflowTag.select().where(WorkflowTag.title == tag["title"])
        if tag_qs.exists():
            tag_row = tag_qs.first()
            workflow.tags.add(tag_row)
            if not tag_row.color.startswith("#"):
                tag_color_count[tag_row.color]+=1
        else:
            if tag.get("color"):
                color = tag.get("color")
                tag_obj = WorkflowTag.create(
                    title=tag["title"],
                    color=color,
                )
                workflow.tags.add(tag_obj)
            else:
                tag_to_add.add(tag["title"])
    for tag in tag_to_add:
        color = sorted(tag_color_count.items(), key=lambda x:x[1])[0][0]
        tag_obj = WorkflowTag.create(
            title=tag,
            color=color,
        )
        tag_color_count[color]+=1
        workflow.tags.add(tag_obj)

def get_webcam_id_by_code(code):
    access_token_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    resp = session.get(access_token_url,params={"corpid":corpid,"corpsecret":corpsecret})
    access_token = resp.json()['access_token']
    user_id_url = 'https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo'
    resp_data = session.get(user_id_url,params={"access_token":access_token,"code":code}).json()
    webcam_id =  resp_data.get('userid',"")
    print(webcam_id)
    return webcam_id

def workflow_record_cleaner(workflow_record):
    for node in workflow_record['data']['nodes']:
        node_values = node['data']['template']
        displayed_values = {}
        show_trigger_values = ["show" in x for x in node_values]
        for value_name,value_detail in node_values.items():
            if value_detail.get('show') or value_detail.get('field_type') not in ["textarea","list",""] or sum(show_trigger_values):
                displayed_values[value_name] = value_detail
        node['data']['template'] = displayed_values

import fcntl
import os

def is_manager(user_id):
    rows = User.select().where(User.user_id == user_id)
    if rows.exists() and rows.first().role and rows.first().role.upper() in ["ROOT","ADMIN"]:
        return True
    else:
        return False

class FileLock:
    def __init__(self, filename):
        self.filename = filename
        self.locked = False
        self.handle = open(filename, 'w')

    def acquire(self):
        try:
            fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.locked = True
            return True
        except IOError:
            return False

    def release(self):
        if not self.locked:
            return
        fcntl.flock(self.handle, fcntl.LOCK_UN)
        self.locked = False

    def __del__(self):
        self.handle.close()
        if os.path.exists(self.filename):
            os.remove(self.filename)
