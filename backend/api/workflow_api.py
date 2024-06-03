import json
import time
import uuid
from pathlib import Path
from datetime import datetime

from peewee import fn, SQL, Case

from models.user_models import User
from models import (
    Workflow,
    WorkflowTag,
    model_serializer,
    WorkflowTemplate,
    WorkflowRunRecord,
    WorkflowRunSchedule,
    OpenAIHistory,
)
from api.utils import get_user_object_general, WorkflowData
from utilities.files import copy_file
from utilities.static_file_server import StaticFileServer
from utilities.tools import tag_register, workflow_record_cleaner,is_manager
from utilities.print_utils import logger
from utilities.workflow import get_workflow_data, save_workflow_data, send_worklow_runinfo_to_mq

from contrib.easy_compressor.flow_shortcut import compress_workflowrunrecord, decompress_flow_data


class WorkflowAPI:
    name = "workflow"

    def restart(self):
        rows = WorkflowRunRecord.select().where(WorkflowRunRecord.status.in_(['QUEUED', 'RUNNING']))
        
        for row in rows:
            # workflow_data = row.data
            workflow_data = decompress_flow_data(compress_id=row.data_id)  # 数据解压
            workflow_data["rid"] = row.rid.hex
            workflow_data['user_id'] = str(row.user_id)
            workflow_data['is_redo'] = True
            row.status = "QUEUED"
            row.save()
            self.worker_queue.put({"data": row.data})
            logger.info(f"restart running workflow, rid:{row.rid}")

    
    def redo(self, payload):
        rid = payload['rid']
        status, msg, origin_record = get_user_object_general(
            WorkflowRunRecord,
            rid=payload.get("rid", None),
        )
        # workflow_data = origin_record.data
        workflow_data = decompress_flow_data(compress_id=origin_record.data_id)  # 数据解压
        status, msg, workflow = get_user_object_general(
            Workflow,
            wid=payload.get("workflow", None).get("wid",None),
        )
        workflow_data["wid"] = workflow.wid.hex
        new_record = WorkflowRunRecord.create(
            workflow=workflow,
            # data=workflow_data,
            user_id=payload.get("user_id", None),
            status="QUEUED",
        )
        # 数据压缩
        compress_workflowrunrecord(wrc_obj=new_record, data=workflow_data)

        workflow_data["rid"] = new_record.rid.hex
        workflow_data['user_id'] = payload.get('user_id','')
        workflow_data['is_redo'] = True

        self.worker_queue.put({"data": workflow_data})
        response = {"status": 200, "msg": "success", "data": {"rid": new_record.rid.hex}}
        return response

    def get(self, payload):
        user_id = payload.get("user_id", None)
        if user_id and not is_manager(user_id):
            status, msg, workflow = get_user_object_general(
                Workflow,
                wid=payload.get("wid", None),
                user_id=user_id
            )
        else:
            status, msg, workflow = get_user_object_general(
                Workflow,
                wid=payload.get("wid", None),
            )

        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response
        workflow = model_serializer(workflow, manytomany=True)
        response = {"status": 200, "msg": "success", "data": workflow}
        return response

    def create(self, payload):
        title = payload.get("title", "").encode("utf16", errors="surrogatepass").decode("utf16")
        brief = payload.get("brief", "").encode("utf16", errors="surrogatepass").decode("utf16")
        images = payload.get("images", [])
        tags = payload.get("tags", [])
        user_id = payload.get("user_id")
        data = payload.get("data", {"nodes": [], "edges": []})
        language = payload.get("language", "zh-CN")

        workflow: Workflow = Workflow.create(
            title=title,
            brief=brief,
            data=data,
            language=language,
            images=images,
            user_id=user_id,
        )
        tag_register(workflow, tags)
        workflow = model_serializer(workflow, manytomany=True)
        response = {"status": 200, "msg": "success", "data": workflow}
        return response

    def update(self, payload):
        wid = payload.get("wid", None)
        status, msg, workflow = get_user_object_general(
            Workflow,
            wid=wid,
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response
        data = payload.get("data", {})
        title = payload.get("title", "").encode("utf16", errors="surrogatepass").decode("utf16")
        brief = payload.get("brief", "").encode("utf16", errors="surrogatepass").decode("utf16")
        images = payload.get("images", [])
        tags = set(payload.get("tags", []))
        tags = [{"title":tag} for tag in tags]
        tag_register(workflow, tags)
        workflow.title = title
        workflow.brief = brief

        related_workflows = WorkflowData(data).related_workflows
        if wid in related_workflows.keys():
            return {"status": 400, "msg": "workflow can not be related to itself", "data": {}}
        data["related_workflows"] = related_workflows

        # Copy images to static folder and store in url format
        copied_images = []
        for image in images:
            if image.startswith("http://localhost"):
                continue
            image_ext = Path(image).resolve().suffix
            image_name = uuid.uuid4().hex + image_ext
            copied_image_path = Path(self.data_path) / "static" / "images" / image_name
            copy_file(image, copied_image_path)
            image_url = StaticFileServer.get_file_url(f"images/{image_name}")
            copied_images.append(image_url)
        workflow.images = copied_images
        workflow.data = data
        workflow.update_time = datetime.now()
        workflow.save()
        response = {"status": 200, "msg": "success", "data": model_serializer(workflow, manytomany=True)}
        return response

    def delete(self, payload):
        status, msg, workflow = get_user_object_general(
            Workflow,
            wid=payload.get("wid", None),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response
        WorkflowRunRecord.delete().where(WorkflowRunRecord.workflow == workflow).execute()
        workflow.delete_instance()
        response = {"status": 200, "msg": "success", "data": {}}
        return response

    def list(self, payload):
        tags = payload.get("tags", [])
        page_num = payload.get("page", 1)
        page_size = min(payload.get("page_size", 10), 100)
        sort_field = payload.get("sort_field", "update_time")
        sort_order = payload.get("sort_order", "descend")
        user_id = payload.get("user_id")
        sort_field = getattr(Workflow, sort_field)
        search_text = payload.get("search_text", "")
        if sort_order == "descend":
            sort_field = sort_field.desc()
        workflows = Workflow.select(
            Workflow.wid,
            Workflow.user,
            Workflow.status,
            Workflow.title,
            Workflow.brief,
            Workflow.images,
            Workflow.language,
            Workflow.is_fast_access,
            Workflow.create_time,
            Workflow.update_time
        ).where(Workflow.user_id == user_id)
        if tags and tags[0]!="all":
            workflows = (
                workflows.join(Workflow.tags.get_through_model())
                .where(Workflow.tags.get_through_model().workflowtag_id.in_(tags))
                .distinct()
            )
        if len(search_text) > 0:
            workflows = workflows.where(
                (fn.Lower(Workflow.title).contains(search_text.lower()))
                | (fn.Lower(Workflow.brief).contains(search_text.lower()))
            )
        workflows_count = workflows.count()
        offset = (page_num - 1) * page_size
        limit = page_size
        workflows = workflows.order_by(sort_field).offset(offset).limit(limit)
        workflows_list = model_serializer(workflows, many=True, manytomany=True)
        response_data = {
            "workflows": workflows_list,
            "total": workflows_count,
            "page_size": page_size,
            "page": page_num,
        }
        if payload.get("need_fast_access", False):
            fast_access_workflows = Workflow.select().where(Workflow.is_fast_access).where(Workflow.user_id == user_id).order_by(sort_field)
            response_data["fast_access_workflows"] = model_serializer(
                fast_access_workflows, many=True, manytomany=True
            )
        response = {
            "status": 200,
            "msg": "success",
            "data": response_data,
        }
        return response

    def run(self, payload):
        status, msg, workflow = get_user_object_general(
            Workflow,
            wid=payload.get("wid", None),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response

        workflow_data = payload.get("data", {})
        workflow_data["wid"] = workflow.wid.hex
        workflow_data['user_id'] = payload.get('user_id','')
        workflow_data['parent_wid'] = payload.get('parent_wid','')

        user_id=payload.get("user_id", None)
        record = WorkflowRunRecord.create(
            workflow=workflow,
            # data=workflow_data,
            user_id=user_id,
            status="QUEUED",
        )
        # 数据压缩
        compress_workflowrunrecord(wrc_obj=record, data=workflow_data)

        try:
            workflow_data["rid"] = record.rid.hex
            save_workflow_data(record.rid.hex, workflow_data)
            send_worklow_runinfo_to_mq(workflow_data)
            logger.info(f"workerflow queue added, request user id:{user_id}, rid:{record.rid.hex}")
        except Exception as e:
            logger.error(f"工作流运行失败, rid:{record.rid}, error:{e}")
            record.status = "FAILED"
            record.general_details["error_detail"] = f"工作流初始化失败. {e}"
            record.save()
            return {"status": 500, "msg": "run failed", "data": {}}
        response = {"status": 200, "msg": "success", "data": {"rid": record.rid.hex}}
        return response

    def check_status(self, payload):
        rid = payload.get("rid", None)
        if rid is None:
            response = {"status": 400, "msg": "rid is None", "data": {}}
            return response
        
        record_qs = WorkflowRunRecord.select(WorkflowRunRecord.status, WorkflowRunRecord.rid, WorkflowRunRecord.workflow).where(WorkflowRunRecord.rid == rid)
        if not record_qs.exists():
            response = {"status": 404, "msg": "record not found", "data": {}}
            return response
        
        record = record_qs.first()
        if record.status == "FINISHED":
            workflow_serializer_data = model_serializer(record.workflow, manytomany=True)
            record = WorkflowRunRecord.get(WorkflowRunRecord.rid == rid)
            # workflow_serializer_data["data"] = record.data
            # 解压等待kafka消费者将结果数据压缩到表中
            time.sleep(1)
            workflow_serializer_data["data"] = decompress_flow_data(compress_id=record.data_id)  # 数据解压
            response = {"status": 200, "msg": record.status, "data": workflow_serializer_data}
        elif record.status in ("RUNNING", "QUEUED"):
            response = {"status": 202, "msg": record.status, "data": {}}
        else:
            response = {"status": 500, "msg": record.status, "data": {}}
        return response

    def add_to_fast_access(self, payload):
        status, msg, workflow = get_user_object_general(
            Workflow,
            wid=payload.get("wid", None),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response 

        workflow.is_fast_access = True
        workflow.save()
        response = {"status": 200, "msg": "success", "data": {}}
        return response

    def delete_from_fast_access(self, payload):
        status, msg, workflow = get_user_object_general(
            Workflow,
            wid=payload.get("wid", None),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response

        workflow.is_fast_access = False
        workflow.save()
        response = {"status": 200, "msg": "success", "data": {}}
        return response


class WorkflowTemplateAPI:
    name = "workflow_template"

    def get(self, payload):
        status, msg, workflow_template = get_user_object_general(
            WorkflowTemplate,
            tid=payload.get("tid", None),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response
        workflow_template = model_serializer(workflow_template, manytomany=True)
        response = {"status": 200, "msg": "success", "data": workflow_template}
        return response

    def add(self, payload):
        status, msg, workflow_template = get_user_object_general(
            WorkflowTemplate,
            tid=payload.get("tid", None),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response
        workflow_template.used_count += 1
        workflow_template.save()
        workflow = Workflow.objects.create(
            title=workflow_template.title,
            brief=workflow_template.brief,
            language=workflow_template.language,
            data=workflow_template.data,
            user_id=payload.get("user_id", None),
        )
        workflow = model_serializer(workflow, manytomany=True)
        response = {"status": 200, "msg": "success", "data": workflow}
        return response

    def list(self, payload):
        page_num = payload.get("page", 1)
        page_size = min(payload.get("page_size", 12), 100)
        sort_field = payload.get("sort_field", "title")
        sort_order = payload.get("sort_order", "ascent")
        tags = payload.get("tags", None)
        search_text = payload.get("search_text", "")
        user_id = payload.get("user_id", "")
        role = User.select().where(User.user_id==user_id).first().role
        if role in ["BLACK_PERSON", "WHITE_USER", "OUTUSER"]:
            response_data = {
            "templates": [],
            "total": 0,
            "page_size": 0,
            "page": 0,
            }
            response = {"status": 200, "msg": "success", "data": response_data}
            return response
        sort_field = sort_field + " desc" if sort_order == "descend" else sort_field
        workflow_templates = WorkflowTemplate.select()
        if tags and tags[0]!="all":
            tag = WorkflowTag.get(WorkflowTag.tid == tags[0])
            workflow_templates = tag.templates
        if len(search_text) > 0:
            workflow_templates = workflow_templates.where(
                (fn.Lower(WorkflowTemplate.title).contains(search_text.lower()))
                | (fn.Lower(WorkflowTemplate.brief).contains(search_text.lower()))
            )
        workflow_templates_count = workflow_templates.count()
        offset = (page_num - 1) * page_size
        limit = page_size
        workflow_templates = workflow_templates.order_by(SQL(sort_field)).offset(offset).limit(limit)
        workflow_templates_list = model_serializer(workflow_templates, many=True, manytomany=True)
        response_data = {
            "templates": workflow_templates_list,
            "total": workflow_templates_count,
            "page_size": page_size,
            "page": page_num,
        }
        response = {"status": 200, "msg": "success", "data": response_data}
        return response
    
    def create(self, payload):
        wid = payload.get("wid", None)
        status, msg, user_workflow = get_user_object_general(
            Workflow,
            wid=wid,
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response

        status, msg, workflow_template = get_user_object_general(
            WorkflowTemplate,
            wid=wid,
        )
        print(workflow_template)
        if not workflow_template:
            workflow_template: WorkflowTemplate = WorkflowTemplate.create(
                user=payload['user_id'],
                title=payload['title'],
                brief=payload['brief'],
                language=payload['language'],
                data = user_workflow.data,
                images = user_workflow.images,
                share_to_community = payload['share_to_community'],
                wid = wid,
            )
            for tag in user_workflow.tags:
                workflow_template.tags.add(tag)
        else:
            querry = WorkflowTemplate.update(
                title=payload['title'],
                brief=payload['brief'],
                language=payload['language'],
                data = user_workflow.data,
                images = user_workflow.images,
                share_to_community = payload['share_to_community'],
            ).where(WorkflowTemplate.wid == wid)
            querry.execute()
            tag_exsit = {tag.title  for tag in workflow_template.tags}
            for tag in user_workflow.tags:
                if tag.title not in tag_exsit:
                    workflow_template.tags.add(tag)

        response_data = {
            "tid": workflow_template.tid,
        }
        response = {"status": 200, "msg": "success", "data": response_data}
        return response
    
    def delete(self, payload):
        status, msg, workflow_template = get_user_object_general(
            WorkflowTemplate,
            tid=payload.get("tid", None),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response
        
        workflow_template.delete_instance()
        response = {"status": 200, "msg": "success", "data": {}}
        return response

class WorkflowRunRecordAPI:
    name = "workflow_run_record"

    def get(self, payload):
        status, msg, workflow = get_user_object_general(
            WorkflowRunRecord,
            rid=payload.get("rid", None),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response
        workflow = model_serializer(workflow, manytomany=True)
        workflow.pop('workflow')
        workflow_record_cleaner(workflow)
        response = {"status": 200, "msg": "success", "data": workflow}
        return response

    def list(self, payload):
        page_num = payload.get("page", 1)
        page_size = min(payload.get("page_size", 10), 100)
        sort_field = payload.get("sort_field", "start_time")
        sort_order = payload.get("sort_order", "descend")
        sort_field = getattr(WorkflowRunRecord, sort_field)
        wid = payload.get("wid", "")
        status = payload.get("status", [])
        if sort_order == "descend":
            sort_field = sort_field.desc()

        records = WorkflowRunRecord.select(
            WorkflowRunRecord.workflow,
            WorkflowRunRecord.start_time,
            WorkflowRunRecord.end_time,
            WorkflowRunRecord.status,
            WorkflowRunRecord.rid,
            WorkflowRunRecord.user,
            WorkflowRunRecord.used_credits,
            WorkflowRunRecord.cost,
            Workflow.wid,
            Workflow.title,
            WorkflowRunRecord.general_details,
            WorkflowRunRecord.data_id,
            WorkflowRunRecord.general_details_id,
        ).where(
            (WorkflowRunRecord.user_id == payload.get("user_id"))).join(Workflow).order_by(sort_field)
        if len(wid) > 0:
            records = records.where((WorkflowRunRecord.workflow == wid)|(WorkflowRunRecord.parent_wid == wid)).order_by(WorkflowRunRecord.parent_wid, WorkflowRunRecord.start_time.desc())
        else:
            records = records.where((WorkflowRunRecord.parent_wid == "")| (WorkflowRunRecord.parent_wid.is_null(True)))
        if status:
            records = records.filter(status__in=status)
        records_count = records.count()
        offset = (page_num - 1) * page_size
        limit = page_size
        records = records.offset(offset).limit(limit)
        records_list = model_serializer(records, many=True, manytomany=True)
        response = {
            "status": 200,
            "msg": "success",
            "data": {
                "records": records_list,
                "total": records_count,
                "page_size": page_size,
                "page": page_num,
            },
        }
        return response


class WorkflowTagAPI:
    name = "workflow_tag"

    def get(self, payload):
        status, msg, workflow_tag = get_user_object_general(
            WorkflowTag,
            tid=payload.get("tid", None),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response
        workflow_tag = model_serializer(workflow_tag)
        response = {"status": 200, "msg": "success", "data": workflow_tag}
        return response

    def list(self, payload):
        data = model_serializer(WorkflowTag.select(), many=True)
        sorted_data = sorted(data, key=lambda x: x.get('order_num'))
        response = {"status": 200, "msg": "success", "data": sorted_data}
        return response

    def delete(self, payload):
        status, msg, workflow_tag = get_user_object_general(
            WorkflowTag,
            tid=payload.get("tid", None),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response
        workflow_tag.delete_instance()
        response = {"status": 200, "msg": "success", "data": {}}
        return response


# TODO: Implement this
class WorkflowRunScheduleAPI:
    name = "workflow_schedule_trigger"

    def update(self, payload):
        user_id=payload.get("user_id",""),
        status, msg, workflow = get_user_object_general(
            Workflow,
            wid=payload.get("wid", None),
            user_id=user_id
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response
        workflow_data = payload.get("data", {})
        workflow.data = workflow_data
        workflow.save()
        workflow_data["wid"] = workflow.wid.hex
        cron_expression = ""

        run_schedule_qs = WorkflowRunSchedule.select().join(Workflow).where((Workflow.id == workflow.id) & (Workflow.user_id==user_id))
        if run_schedule_qs.exists():
            run_schedule = run_schedule_qs.first()
            run_schedule.cron_expression = cron_expression
            run_schedule.data = workflow_data
            run_schedule.save()
        else:
            run_schedule = WorkflowRunSchedule.create(
                workflow=workflow,
                cron_expression=cron_expression,
                data=workflow_data,
            )
        # minute, hour, day_of_month, month_of_year, day_of_week = cron_expression.split(" ")
        # timezone = pytz.timezone(payload.get("timezone", "Asia/Shanghai"))
        # TODO: Add to scheduler
        response = {"status": 200, "msg": "success", "data": {}}
        return response

    def delete(request):
        status, msg, workflow = get_user_object_general(
            Workflow,
            wid=request.data.get("wid", None),
            user_id=request.data.get("user_id",""),
        )
        if status != 200:
            response = {"status": status, "msg": msg, "data": {}}
            return response

        run_schedule_qs = WorkflowRunSchedule.select().join(Workflow).where((Workflow.id == workflow.id) & (Workflow.user_id == workflow.user_id))
        if not run_schedule_qs.exists():
            response = {"status": 404, "msg": "run schedule not found", "data": {}}
            return response

        run_schedule = run_schedule_qs.first()
        # TODO: Remove from scheduler
        run_schedule.delete()
        response = {"status": 200, "msg": "success", "data": {}}
        return response
