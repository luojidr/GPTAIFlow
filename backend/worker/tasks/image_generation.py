import uuid
import base64
from pathlib import Path
from utilities.workflow import Workflow
from utilities.web_crawler import proxies
from utilities.static_file_server import StaticFileServer
from worker.tasks import task
import requests
from utilities.print_utils import logger
session = requests.Session()

SAMPLER_MAP = {
    "ddim": "DDIM",
    "plms": "PLMS",
    "k_euler": "Euler",
    "k_euler_ancestral": "Euler a",
    "k_heun": "Heun",
    "k_dpm_2": "DPM2",
    "k_dpm_2_ancestral": "DPM2 a",
    "k_dpmpp_2s_ancestral": "DPM++ 2S a",
    "k_dpmpp_2m": "DPM++ 2M",
    "k_dpmpp_sde": "DPM++ SDE",
}


@task
def stable_diffusion(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    input_prompt = workflow.get_node_field_value(node_id, "prompt")
    input_negative_prompt = workflow.get_node_field_value(node_id, "negative_prompt")
    model = workflow.get_node_field_value(node_id, "model")
    cfg_scale = workflow.get_node_field_value(node_id, "cfg_scale")
    sampler = SAMPLER_MAP[workflow.get_node_field_value(node_id, "sampler")]
    width = workflow.get_node_field_value(node_id, "width")
    height = workflow.get_node_field_value(node_id, "height")
    output_type = workflow.get_node_field_value(node_id, "output_type")

    image_folder = Path("./data") / "static" / "images"
    stable_diffusion_base_url = workflow.setting.get("stable_diffusion_base_url").rstrip("/")

    url = f"{stable_diffusion_base_url}/sdapi/v1/txt2img"

    if isinstance(input_prompt, str):
        prompts = [input_prompt]
    elif isinstance(input_prompt, list):
        prompts = input_prompt

    if isinstance(input_negative_prompt, str):
        negative_prompts = [input_negative_prompt]
    elif isinstance(input_negative_prompt, list):
        negative_prompts = input_negative_prompt

    if len(prompts) < len(negative_prompts) and len(prompts) == 1:
        prompts = prompts * len(negative_prompts)
    elif len(prompts) > len(negative_prompts) and len(negative_prompts) == 1:
        negative_prompts = negative_prompts * len(prompts)

    results = []
    for index, prompt in enumerate(prompts):
        data = {
            "prompt": prompt,
            "negative_prompt": negative_prompts[index],
            "sampler_index": sampler,
            "steps": 30,
            "width": width,
            "height": height,
            "cfg_scale": cfg_scale,
        }
        response = requests.post(url, json=data, proxies=proxies(), timeout=None)
        image_base64 = response.json()["images"][0]
        image_name = f"{uuid.uuid4().hex}.jpg"
        local_file = image_folder / image_name
        with open(local_file, "wb") as image_file:
            image_file.write(base64.b64decode(image_base64))
        results.append(StaticFileServer.get_file_url(f"images/{image_name}"))

    output = results[0] if isinstance(input_prompt, str) else results
    if output_type == "only_link":
        workflow.update_node_field_value(node_id, "output", output)
    elif output_type == "markdown":
        workflow.update_node_field_value(node_id, "output", f"![{output}]({output})")
    elif output_type == "html":
        workflow.update_node_field_value(node_id, "output", f'<img src="{output}"/>')

    workflow.set_node_status(node_id, 200)
    return workflow.data

@task
def dall_e(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    input_prompt = workflow.get_node_field_value(node_id, "prompt")
    size = workflow.get_node_field_value(node_id, "size")
    quality = workflow.get_node_field_value(node_id, "quality")
    style = workflow.get_node_field_value(node_id, "style")
    output_type = workflow.get_node_field_value(node_id, "output_type")
    model = workflow.get_node_field_value(node_id, "model")
    
    api_base = workflow.setting.get("openai_api_base", "https://oneapi.crotondata.cn/v1")
    api_key = workflow.setting.get("openai_api_key")
    url = f"{api_base}/images/generations"
    headers= { "Authorization": "Bearer "+api_key, "Content-Type": "application/json" }
    
    if isinstance(input_prompt, str):
        prompts = [input_prompt]
    elif isinstance(input_prompt, list):
        prompts = input_prompt

    results = []
    record_id = workflow.record_id
    for prompt in prompts:
        body = {
            # Enter your prompt text here
            "prompt": prompt,
            "model":model,
            "size": size, # supported values are “1792x1024”, “1024x1024” and “1024x1792” 
            "n": 1,
            "quality": quality, # Options are “hd” and “standard”; defaults to standard 
            "style": style # Options are “natural” and “vivid”; defaults to “vivid”
        }
        logger.info(f"dall-e-3 request sended, record_id {record_id}, prompt {prompt}")
        submission = session.post(url, headers=headers, json=body)
        if submission.status_code != 200:
            if submission.json()['error']["code"] == "contentFilter":

                logger.info(f"提示词未通过内容审核：{prompt}")
                raise Exception("dall-e-3提示词内容审核未通过，请重试或调整提示词")
            else:
                raise Exception(f"dall-e-3 request failed, error details:{submission.json()['error']}")
        output = submission.json()['data'][0]['url']
        logger.info(f"dall-e-3 request ended, record_id {record_id}")
        results.append(output)
    
    if output_type == "only_link":
        output = results[0] if isinstance(input_prompt, str) else results
        workflow.update_node_field_value(node_id, "output", output)
    else:
        output = ""
        for result in results:
            if output_type == "markdown":
                output+= f"![{result}]({result})\n"
            elif output_type == "html":
                output+= f'<img src="{result}"/>'
        workflow.update_node_field_value(node_id, "output", output)
    # if output_type == "only_link":
    #     workflow.update_node_field_value(node_id, "output", output)
    # elif output_type == "markdown":
    #     workflow.update_node_field_value(node_id, "output", f"![{output}]({output})")
    # elif output_type == "html":
    #     workflow.update_node_field_value(node_id, "output", f'<img src="{output}"/>')

    workflow.set_node_status(node_id, 200)
    return workflow.data
