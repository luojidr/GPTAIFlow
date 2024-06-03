# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-04-13 15:43:01
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-08-24 17:48:44
from utilities.workflow import Workflow
from utilities.print_utils import logger
from models.base import database
from utilities.print_utils import logger
import uuid


class Task:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def s(self, *args, **kwargs):
        return (self, args, kwargs)


def task(func):
    return Task(func)

import func_timeout
class Chain:
    def __init__(self, *tasks):
        self.tasks = tasks

    def __call__(self, initial_data):
        result = initial_data
        for task, args, kwargs in self.tasks:
            for i in range(3):
                try:
                    database.close()
                except:
                    pass
                try:
                    database.connect()
                    uid = uuid.uuid4()
                    logger.info(f"task start, task:{task.func.__name__}, uuid={uid}")
                    result = task(result, *args, **kwargs)
                    logger.info(f"task end, task:{task.func.__name__}, uuid={uid}")
                    database.close()
                    break
                except Exception as e:
                    e.task_name = task.func.__name__
                    if i ==2:
                        raise e
                except func_timeout.FunctionTimedOut:
                    e = Exception("openai 未响应请求，超时跳出")
                    e.task_name = task.func.__name__
                    if i ==2:
                        raise e

        return result


def chain(*tasks):
    return Chain(*tasks)


@task
def on_finish(workflow_data: dict):
    workflow = Workflow(workflow_data)
    workflow.update_original_workflow_data()
    workflow.clean_workflow_data()
    workflow.report_workflow_status(200)
    return True


def on_error(*args, **kwargs):
    logger.error(f"workflow error: {args}, {kwargs}")
    workflow_data = args[-1]
    workflow = Workflow(workflow_data)
    workflow.report_workflow_status(500)
    return True
