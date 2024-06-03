import os
import time
import json
import random
import mimetypes
from typing import Union

import requests
from openai import OpenAI

from utilities.redis_utils import cache
from utilities.workflow import Workflow
from utilities.embeddings import get_token_counts
from utilities.web_crawler import proxies, proxies_for_requests
from utilities.print_utils import logger
from worker.tasks import task
from models.database_models import OpenAIHistory
from models.workflow_models import WorkflowRunRecord 
from models.user_models import User
from contrib.easy_compressor.flow_shortcut import compress_openaihistory

ASR_URL = os.environ.get("ASR_URL")    

model_max_tokens_map = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-4": 131072,
    "gpt-4-32k": 32768,
    "moonshot-v1-128k": 131072,
}
model_tokens_input_cost_map = {
    "gpt-3.5-turbo": 0.0015 / 1000,
    "gpt-3.5-turbo-16k": 0.003 / 1000,
    "gpt-4": 0.01 / 1000,
    "gpt-4-32k": 0.06 / 1000,
    "moonshot-v1-128k": 0.012 / 1000,
}

model_tokens_output_cost_map = {
    "gpt-3.5-turbo": 0.002 / 1000,
    "gpt-3.5-turbo-16k": 0.004 / 1000,
    "gpt-4": 0.03 / 1000,
    "gpt-4-32k": 0.12 / 1000,
    "moonshot-v1-128k": 0.012 / 1000,
}

# azure_model_map = {
#     "gpt-3.5-turbo": "gpt-35-turbo",
#     "gpt-3.5-turbo-16k": "gpt-35-turbo-16k",
#     "gpt-4": 'gpt-4-1106',
#     "gpt-4-32k": 'gpt-4-32k',
#     "moonshot-v1-128k": "moonshot-v1-128k"
# }

oneapi_model_map = {
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k": "gpt-3.5-turbo-16k",
    "gpt-4": 'gpt-4-1106-preview',
    "gpt-4-32k": 'gpt-4-32k',
    "moonshot-v1-128k": "moonshot-v1-128k"
}

from func_timeout import func_set_timeout

# @func_set_timeout(900)
# @set_cache
def openai_chat_creat(client,rid,*args, **kwargs):
    return client.chat.completions.create(*args, **kwargs), False


#@func_set_timeout(900)
@cache
def cached_openai_chat_creat(client,rid,*args, **kwargs):
    return client.chat.completions.create(*args, **kwargs)


@task
def open_ai(
    workflow_data: dict,
    node_id: str,
):
    import openai
    from openai import OpenAI,AzureOpenAI
    workflow = Workflow(workflow_data)
    record_id = workflow.record_id
    
    input_prompt: Union[str, list] = workflow.get_node_field_value(node_id, "prompt")
    temperature: float = workflow.get_node_field_value(node_id, "temperature")
    ignore_error_rate: float = workflow.get_node_field_value(node_id, "ignore_error", default=0.2)
    #openai_api_type = workflow.setting.get("openai_api_type")
    #if openai_api_type == "azure":
    openai.api_type = "azure"
    openai.api_base = workflow.setting.get("azure_openai_api_base")
    openai.api_version = "2023-12-01-preview"
    model = workflow.get_node_field_value(node_id, "llm_model")
    api_base = workflow.setting.get("openai_api_base", "https://oneapi.crotondata.cn/v1")
    api_key = workflow.setting.get("openai_api_key")

    azure_client = AzureOpenAI(
        api_key=workflow.setting.get("azure_openai_api_key"),
        api_version="2023-12-01-preview",
        azure_endpoint = workflow.setting.get("azure_openai_api_base")
    )

    moon_client = OpenAI(
        api_key="Y2tpMGFiYjNhZXNsZ2xqNmZwb2c6bXNrLU1HMlJnQmRIaHNyMkt0UjJCeFpndGpGRlpKYVo=",
        base_url="https://api.moonshot.cn/v1",
    )
    
    client = OpenAI(
        api_key=api_key,
        base_url=api_base,
    )
    if "moon" in model:
        client = moon_client


    oneapi_model_name = oneapi_model_map.get(model)
    engine_model_param = {"model": oneapi_model_name}
    model_max_tokens = model_max_tokens_map.get(model, 4096)
    #print(openai.api_base,openai.api_key)
    # else:
    #     openai.api_type = "open_ai"
    #     openai.api_base = workflow.setting.get("openai_api_base", "https://api.openai.com/v1")
    #     openai.api_version = None
    #     model = workflow.get_node_field_value(node_id, "llm_model")
    #     engine_model_param = {"model": model}
    #     model_max_tokens = model_max_tokens_map.get(model, 4096)
    #     openai.api_key = workflow.setting.get("openai_api_key")
    openai.proxy = proxies_for_requests()
    if isinstance(input_prompt, str):
        prompts = [input_prompt]
    elif isinstance(input_prompt, list):
        prompts = input_prompt
    results = []
    cost = 0
    prompt_number = len(prompts)
    error_prompts = 0
    for prompt in prompts:
        messages = [
            {
                "role": "system",
                "content": prompt,
            },
        ]
        token_counts = get_token_counts(prompt)
        #用于控制 open ai 请求的并发
        lock_key = str(random.randint(0,3)) +str(time.time())
        # lock = GlobalLockPool(redis_conn,lock_key,lock_num=3)
        # lock.acquire()
        logger.info(f'start a new open ai {model} request from {record_id} index_id {lock_key}  token_counts : {token_counts} ')
        max_tokens = model_max_tokens - token_counts - 50
        # chat_creat_func = cached_openai_chat_creat #if workflow.is_redo else openai_chat_creat
        chat_creat_func = openai_chat_creat if int(temperature) == 1 else openai_chat_creat
        # for i in range(3):
        try:
            if 'gpt-4' in model.lower():
                response,use_cache = chat_creat_func(
                    client,
                    workflow.record_id,
                    **engine_model_param,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=min(max_tokens, 4096),
                    # top_p=0.77,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                )   
            else:
                response,use_cache = chat_creat_func(
                    client,
                    workflow.record_id,
                    **engine_model_param,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=0.95 , 
                    frequency_penalty=0,
                    presence_penalty=0,
                )   
            # break
        except Exception as e:
            logger.error(f"openai api failed, rid:{record_id}, message:"+str(e))
            error_code = e.code if hasattr(e,"code") else None
            time.sleep(60)
        try:
            choice = response.choices[0]
            result = choice.message.content
            if result is None:
                if choice.finish_reason == "content_filter":
                    error_code="content_filter"
                    raise ValueError("调用 open ai 接口返回内容被过滤")
        except Exception as e:
            logger.info(e)
            logger.error(f'failed to get openai request from {record_id} index_id {lock_key}  token_counts : {token_counts} prompt: {str(prompt)}')
            error_prompts+=1
            result=""
            use_cache=False
            if  error_prompts/prompt_number > ignore_error_rate:
                if error_code=="content_filter":
                    e = ValueError("调用 open ai 接口返回内容被过滤")
                    e.error_detail = f'调用 open ai 接口因prompt未通过内容审核导致失败，请检查prompt是否包含敏感内容，prompt: {prompt}'
                    # e.error_code = 501
                    raise e 
                elif error_code=="context_length":
                    e = ValueError("调用 open ai 接口返回内容长度超过限制")
                    e.error_detail= f'调用 open ai 内容长度超过限制，prompt: {prompt}'
                    # e.error_code = 501
                    raise e 
                e = ValueError("调用 open ai 接口超时或失败")
                e.error_detail = f'调用 open ai 接口超时或失败, 使用模型{model}, token_counts : {token_counts}'
                # e.error_code = 501
                raise e 
        # result = prompt[:100]
        # use_cache = True
        logger.info(f'end a new open ai request from {record_id} index_id {lock_key} from catch {use_cache} ')
        try:
            output_tokens = get_token_counts(result)
        except Exception as e:
            logger.error(f'error result:{result} ,rid:{workflow.record_id}, error: {e}')
            continue
        if not use_cache:
            cost += model_tokens_input_cost_map.get(model, 0) * token_counts + model_tokens_output_cost_map.get(model, 0) * output_tokens
            record = OpenAIHistory.create(
                chat_id=record_id+lock_key,
                user_id=workflow.data.get('user_id'),
                input_tokens=token_counts,
                output_tokens=output_tokens,
                # input_str=prompt,
                # output_str=result,
                model_type=model.lower(),
                rid=workflow.record_id,
            )
            # 数据压缩
            compress_openaihistory(record, input_str=prompt, output_str=result)

        results.append(result)

    user_obj = User.get(User.user_id == workflow.data.get('user_id'))
    if user_obj.cost is None:
        user_obj.cost = cost
    else:
        user_obj.cost += cost
    user_obj.save()

    workflow_obj = WorkflowRunRecord.select(WorkflowRunRecord.cost).where(WorkflowRunRecord.rid == workflow.record_id).first()
    workflow_cost = workflow_obj.cost if workflow_obj and workflow_obj.cost else 0
    workflow_cost += cost
    WorkflowRunRecord.update(cost=workflow_cost).where(WorkflowRunRecord.rid == workflow.record_id).execute()
    output = results[0] if isinstance(input_prompt, str) else results
    workflow.update_node_field_value(node_id, "output", output)
    workflow.set_node_status(node_id, 200)
    return workflow.data


@task
def chat_glm(
    workflow_data: dict,
    node_id: str,
):
    logger.info(f"start a new chat glm task for node {node_id}")
    workflow = Workflow(workflow_data)
    input_prompt: Union[str, list] = workflow.get_node_field_value(node_id, "prompt")
    temperature: float = workflow.get_node_field_value(node_id, "temperature")
    model = workflow.get_node_field_value(node_id, "llm_model")
    if model == "chatglm-6b":
        api_base = workflow.setting.get("chatglm6b_api_base")
    else:
        raise ValueError("model not supported")

    if isinstance(input_prompt, str):
        prompts = [input_prompt]
    elif isinstance(input_prompt, list):
        prompts = input_prompt

    results = []
    for prompt in prompts:
        messages = {"prompt": prompt, "history": [], "temperature": temperature}
        response = requests.post(api_base, json=messages, proxies=proxies(), timeout=None)
        result = response.json()["response"]
        results.append(result)

    output = results[0] if isinstance(input_prompt, str) else results
    workflow.update_node_field_value(node_id, "output", output)
    workflow.set_node_status(node_id, 200)
    logger.info(f"end a new chat glm task for node {node_id}")
    return workflow.data

@task
def baichuan(
    workflow_data: dict,
    node_id: str,
):
    logger.info(f"start a new baichuan task for node {node_id}")
    workflow = Workflow(workflow_data)
    input_prompt: Union[str, list] = workflow.get_node_field_value(node_id, "prompt")
    temperature: float = workflow.get_node_field_value(node_id, "temperature")
    model = workflow.get_node_field_value(node_id, "llm_model")
    #api_base = 'http://127.0.0.1:8333/baichuan2'
    if isinstance(input_prompt, str):
        prompts = [input_prompt]
    elif isinstance(input_prompt, list):
        prompts = input_prompt

    results = []
    if model == "baichuan-13b":
        api_base = workflow.setting.get("baichuan13b_api_base")
        for prompt in prompts:
            messages = {"prompts": prompt, "history": [], "temperature": temperature}
            succ = False
            #response = post(api_base,message=messages)
            for i in range(3):
                try:
                    response = requests.post(api_base, json=messages, proxies=proxies(), timeout=None)
                    #print(response.json())
                    result = response.json()["data"]["response"]
                    results.append(result)
                    succ = True
                    break
                except Exception as e:
                    logger.error('baichuan llm failed' + str(e))
                    time.sleep(5)
            if not succ:
                e = Exception
                e.error_detail = '调用百川模型失败'
                raise e
    elif model == "baichuan2-13b":
        api_base = workflow.setting.get("baichuan2_13b_api_base")
        api_key = workflow.setting.get("baichuan2_13b_api_key")
        for prompt in prompts:
            payload = json.dumps({
                "model": "baichuan2-13b",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": temperature,
                "stream": False
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {api_key}"
            }
            try:
                response = requests.request("POST", api_base, headers=headers, data=payload, timeout=900)
                result = response.json()["choices"][0]["message"]["content"]
                results.append(result)
            except Exception as e:
                logger.error('baichuan2 llm failed' + str(e))
                e = ValueError("调用 baichuan2 接口超时或失败")
                e.error_detail = '调用baichuan2失败'
                raise e
    else:
        raise ValueError("model not supported")
    output = results[0] if isinstance(input_prompt, str) else results
    workflow.update_node_field_value(node_id, "output", output)
    workflow.set_node_status(node_id, 200)
    logger.info(f"end a new baichuan task for node {node_id}")
    return workflow.data

@task
def webpilot(
    workflow_data: dict,
    node_id: str,
):
    logger.info(f"start a new webpilot task for node {node_id}")
    workflow = Workflow(workflow_data)
    input_prompt: Union[str, list] = workflow.get_node_field_value(node_id, "prompt")
    model = workflow.get_node_field_value(node_id, "llm_model")
    api_base = "https://beta.webpilotai.com/api/v1/watt"
    api_key = "8b1d5fb8d1b04463a54aacfd5d957063"
    headers = {"Authorization": f"Bearer {api_key}"}
    if isinstance(input_prompt, str):
        prompts = [input_prompt]
    elif isinstance(input_prompt, list):
        prompts = input_prompt

    results = []
    for prompt in prompts:
        messages = {"content": prompt, "model": model}
        succ = False
        #response = post(api_base,message=messages)
        try:
            response = requests.post(api_base, json=messages, headers=headers, proxies=proxies(), timeout=None)
            #print(response.json())
            result = response.json()["content"]
            results.append(result)
        except Exception as e:
            logger.error('webpilot failed' + str(e))
            e = ValueError("调用 open ai 接口超时或失败")
            e.error_detail = '调用webpilot失败'
            raise e
    output = results[0] if isinstance(input_prompt, str) else results
    workflow.update_node_field_value(node_id, "output", output)
    workflow.set_node_status(node_id, 200)
    logger.info(f"end a new webpilot task for node {node_id}")
    return workflow.data

@task
def asrparaformer(
    workflow_data: dict,
    node_id: str,
):
    logger.info(f"start a new asr_paraformer task for node {node_id}")
    files = []
    workflow = Workflow(workflow_data)
    input_prompt: Union[str, list] = workflow.get_node_field_value(node_id, "prompt")
    for file_path in input_prompt:
        file_type, _ = mimetypes.guess_type(file_path)
        files.append(("voice_file_list",(file_path, open(file_path, 'rb'), file_type)))
    res = []
    try:
        response = requests.post(ASR_URL, files=files, timeout=None)
        # print(response.json())
        logger.info(response.json())
        result = response.json()
        res.append(result.get("result"))
    except Exception as e:
        logger.error('paraformer failed' + str(e))
        e = ValueError("调用 paraformer 接口超时或失败")
        e.error_detail = '调用paraformert失败'
        raise e
    workflow.update_node_field_value(node_id, "output", res)
    workflow.set_node_status(node_id, 200)
    logger.info(f"end a new paraformer task for node {node_id}")
    return workflow.data


@task
def deepSeek(
    workflow_data: dict,
    node_id: str,
):
    logger.info(f"start a new deepSeek task for node {node_id}")
    workflow = Workflow(workflow_data)
    input_prompt: Union[str, list] = workflow.get_node_field_value(node_id, "prompt")
    model = workflow.get_node_field_value(node_id, "llm_model")
    api_base = workflow.setting.get("deepSeek_api_base")
    api_key = workflow.setting.get("deepSeek_api_key")
    headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(api_key)
              }
    error_count = 0
    if isinstance(input_prompt, str):
        prompts = [input_prompt]
    elif isinstance(input_prompt, list):
        prompts = input_prompt

    results = []
    for prompt in prompts:
        messages = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ]
                }
        try:
            response = requests.post(api_base, data=json.dumps(messages), headers=headers, proxies=proxies(), timeout=None)
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                results.append(result)
            else:
                logger.error(f"deepSeek服务调用失败，{response.json()}")
                if response.json().get("detail") == "Content Exists Risk":
                    error_count+=1
        except Exception as e:
            logger.error('deepSeek failed ' + str(e))
            e = ValueError("调用 open ai 接口超时或失败")
            e.error_detail = '调用deepSeek失败'
            raise e
    if error_count / len(prompts) > 0.2:
        raise ValueError("调用deepSeek失败")
    output = results[0] if isinstance(input_prompt, str) else results
    workflow.update_node_field_value(node_id, "output", output)
    workflow.set_node_status(node_id, 200)
    logger.info(f"end a new deepSeek task for node {node_id}")
    return workflow.data


@task
def Qwen(
    workflow_data: dict,
    node_id: str,
):
    logger.info(f"start a new Qwen task for node {node_id}")
    workflow = Workflow(workflow_data)
    input_prompt: Union[str, list] = workflow.get_node_field_value(node_id, "prompt")
    model = workflow.get_node_field_value(node_id, "llm_model")
    if model == "qwen-32":
        model = "Qwen/Qwen1.5-32B-Chat"
        api_base = workflow.setting.get("Qwen-32_api_base", "http://192.168.191.56:8032/v1")
    else:
        api_base = workflow.setting.get("Qwen-110_api_base", "http://192.168.191.56:8034/v1")
        model = "Qwen/Qwen1.5-110B-Chat"
    api_key = workflow.setting.get("Qwen_api_key", "sk-ac9a720d0e93439abcd838a9899fb87f")
    error_count = 0
    if isinstance(input_prompt, str):
        prompts = [input_prompt]
    elif isinstance(input_prompt, list):
        prompts = input_prompt

    results = []
    for prompt in prompts:
        try:
            client = OpenAI(
            api_key=api_key,
                base_url=api_base,
                )
            chat_completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": 'You are a helpful assistant. '},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7
            )
            response = chat_completion.choices[0].message.content
            results.append(response)
        except Exception as e:
            logger.error('Qwen failed ' + str(e))
            e = ValueError("调用 open ai 接口超时或失败")
            e.error_detail = '调用Qwen失败'
            raise e
    if error_count / len(prompts) > 0.2:
        raise ValueError("调用Qwen失败")
    output = results[0] if isinstance(input_prompt, str) else results
    workflow.update_node_field_value(node_id, "output", output)
    workflow.set_node_status(node_id, 200)
    logger.info(f"end a new Qwen task for node {node_id}")
    return workflow.data
