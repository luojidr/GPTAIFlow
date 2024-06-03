from worker.tasks import task
from utilities.workflow import Workflow
import requests
from utilities.print_utils import logger
import os
import base64
import hashlib
from config import PORT,SERVER_DOMAIN
session = requests.Session()

TMP_FILE_DIR = 'tmp_data/files/'
@task
def tts(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    record_id = workflow.get_node_field_value(node_id, "record_id")
    input = workflow.get_node_field_value(node_id, "input")
    voice = workflow.get_node_field_value(node_id, "voice")
    model = workflow.get_node_field_value(node_id, "model")

    
    params = {"api-version":"2024-02-15-preview"}
    api_key = "77466f5fe1414df29fedffdb98e132e9"
    url = "https://croton-sweden2.openai.azure.com//openai/deployments/tts/audio/speech"
    headers= { "api-key": api_key, "Content-Type": "application/json" }
    

    body = {
        "model": model,
        "input": input, # Options are “hd” and “standard”; defaults to standard 
        "voice": voice # Options are “natural” and “vivid”; defaults to “vivid”
    }
    logger.info(f"tts request sended, record_id {record_id}, body {body}")
    response = session.post(url, headers=headers, params=params, json=body)
    file_name = hashlib.sha256(response.content).hexdigest()
    logger.info(f"tts request ended, record_id {record_id}")
    os.makedirs(TMP_FILE_DIR, exist_ok=True)
    file_path = TMP_FILE_DIR+str(file_name)+(".mp3")
    with open(file_path, 'wb') as file:
        file.write(response.content)
    logger.info(f"文件已保存为: {file_path}")
    # markdown_content = f"""
    # <audio controls>
    # <source src="http://{SERVER_DOMAIN}:{PORT}/files/{file_name}.mp3" type="audio/mpeg">
    #     Your browser does not support the audio element.
    # </audio>
    # <a href="http://{SERVER_DOMAIN}:{PORT}/files/{file_name}.mp3" download>下载音频</a>
    # """
    markdown_content = f"[下载音频](http://{SERVER_DOMAIN}:{PORT}/files/{file_name}.mp3)"
    workflow.update_node_field_value(node_id, "output", markdown_content)

    workflow.set_node_status(node_id, 200)
    return workflow.data