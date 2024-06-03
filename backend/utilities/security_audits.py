# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
from config import SECRET_ID, SECRET_KEY, REGION, BUCKET_NAME
from utilities.print_utils import logger
import traceback

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


cheme = 'https'
user_info = {}

config = CosConfig(Region=REGION, SecretId=SECRET_ID, SecretKey=SECRET_KEY, Scheme="https")
client = CosS3Client(config)

label_result = {
    'Normal': "正常",
    'Porn': "色情",
    'Ads': "广告或其他",
    'Politics': "政治",
    "Spam": "垃圾信息",
    "Terrorism": "暴恐",
    "Abuse": "辱骂",
    "Flood": "水军相关（刷屏、灌水）",
    "Contraband": "违禁品",
    "Meaningless": "垃圾"
}

def check_content(content):
    logger.info("开始对输入内容进行安全校验")
    try:
        content_len = len(content)
        if content_len > 10000:
            results = [content[i:i+10000] for i in range(0, len(content), 10000)]
        else:
            results = [content]
        flag = True
        labels = []
        for res in results:
            response = client.ci_auditing_text_submit(
                Bucket=BUCKET_NAME, 
                Content=res.encode("utf-8"), 
                BizType='',
                UserInfo=user_info,
                DataId='hc-safe',
            )
            request_id = response.get('RequestId')
            job_id = response.get("JobsDetail").get('JobId')
            state = response.get("JobsDetail").get("State")
            if state == "Failed":
                message = response.get("Message")
                logger.error(f"RequestId：{request_id}，JobId： {job_id} 调用安全校验接口失败，失败原因: {message}")
                raise ValueError(f'调用安全校验接口失败，失败原因: {message}')
            else:
                logger.info(f"RequestId：{request_id}，JobId： {job_id} 调用安全校验接口成功")
                label = response.get("JobsDetail").get("Label")
                if label == "Normal":
                    continue
                flag = False
                # label = label_result[label]
                # if label not in labels:
                #     labels.append(label)
                
        if flag:
            return ""
        else:
            msg = '对不起，上述问题的解决都超出我的能力范围'
            logger.info(f'{msg}')
            return msg
    except Exception as e:
        logger.error(f"文本校验失败，失败原因: {traceback.format_exc()}")
        raise ValueError(f'文本校验失败，失败原因: {e}')




