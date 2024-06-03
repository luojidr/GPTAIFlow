# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-05-16 18:54:18
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-08-07 01:19:22
from datetime import datetime
import random
import re
import json
import time
import base64
import urllib.request
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os
from pathlib import Path
import traceback

# import httpx
import requests
from bs4 import BeautifulSoup
from models.workflow_models import WorkflowRunRecord
from readability import Document
from markdownify import MarkdownConverter, chomp
import pymysql
import config
from models import Setting, model_serializer
from utilities.print_utils import logger

from contrib.easy_compressor.flow_shortcut import compress_workflowrunrecord, decompress_flow_data

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

http_proxy_host_re = re.compile(r"http.*://(.*?)$")


def proxies():
    try:
        if Setting.select().count() == 0:
            setting = Setting.create()
        else:
            setting = Setting.select().order_by(Setting.create_time.desc()).first()
        setting = model_serializer(setting)
    except Exception as e:
        logger.error(e)
        return {}
    if not setting.get("data", {}).get("use_system_proxy"):
        return {}
    else:
        system_proxies = urllib.request.getproxies()
        proxies = {}
        for protocol, proxy in system_proxies.items():
            http_proxy_host = http_proxy_host_re.findall(proxy)
            if not http_proxy_host:
                continue
            proxy_url = f"http://{http_proxy_host[0]}"
            proxies[f"{protocol}://"] = proxy_url
        return proxies


def proxies_for_requests():
    try:
        if Setting.select().count() == 0:
            setting = Setting.create()
        else:
            setting = Setting.select().order_by(Setting.create_time.desc()).first()
        setting = model_serializer(setting)
    except Exception as e:
        logger.error(e)
        return {}
    if not setting.get("data", {}).get("use_system_proxy"):
        return {}
    else:
        system_proxies = urllib.request.getproxies()
        proxies_for_requests = {}
        for protocol, proxy in system_proxies.items():
            http_proxy_host = http_proxy_host_re.findall(proxy)
            if not http_proxy_host:
                continue
            proxy_url = f"http://{http_proxy_host[0]}"
            proxies_for_requests[protocol] = proxy_url
        return proxies_for_requests


logger.info(f"Proxies: {proxies()}")
logger.info(f"Proxies for requests: {proxies_for_requests()}")


def decrypt_aes_ecb_base64(ciphertext_base64, key):
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = base64.b64decode(ciphertext_base64)
    return unpad(cipher.decrypt(ciphertext), AES.block_size).decode("utf-8")


class CustomMarkdownConverter(MarkdownConverter):
    def convert_b(self, el, text, convert_as_inline):
        return self.custom_bold_conversion(el, text, convert_as_inline)

    convert_strong = convert_b

    def custom_bold_conversion(self, el, text, convert_as_inline):
        markup = 2 * self.options["strong_em_symbol"]
        prefix, suffix, text = chomp(text)
        if not text:
            return ""
        return "%s%s%s%s%s " % (prefix, markup, text, markup, suffix)


def markdownify(html, **options):
    return CustomMarkdownConverter(**options).convert(html)


def clean_markdown(text: str):
    content = "\n\n".join([s.strip() for s in text.split("\n") if s.strip()])
    content = content.replace("![]()", "").replace("*\n", "")
    content = "\n\n".join([s.strip() for s in content.split("\n") if s.strip()])
    return content


def crawl_text_from_url(url: str):
    if not url.startswith("http"):
        url = f"http://{url}"

    try_times = 0
    crawl_success = False
    while try_times < 5:
        try:
            response = requests.get(url, headers=headers, proxies=proxies(), allow_redirects=True)
            crawl_success = True
            break
        except Exception as e:
            logger.error(e)
            try_times += 1
            time.sleep(1)

    if not crawl_success:
        raise Exception("Crawl failed")

    if "https://mp.weixin.qq.com/" in url:
        soup = BeautifulSoup(response.content, "lxml")
        content = str(soup.select_one("#js_content"))
        content = clean_markdown(markdownify(content))
        result = {
            "title": soup.select_one("#activity-name").text.strip(),
            "text": content,
            "url": url,
        }
    elif url.startswith("https://zhuanlan.zhihu.com"):
        soup = BeautifulSoup(response.text, "lxml")
        content = str(soup.select_one(".Post-RichText"))
        content = clean_markdown(markdownify(content))
        result = {
            "title": soup.select_one(".Post-Title").text.strip(),
            "text": content,
            "url": url,
        }
    elif url.startswith("https://www.zhihu.com/question/"):
        soup = BeautifulSoup(response.text, "lxml")
        content = soup.select_one(".RichContent-inner")
        for style in content.select("style"):
            style.decompose()
        content = str(content)
        content = clean_markdown(markdownify(content))
        result = {
            "title": soup.select_one(".QuestionHeader-title").text.strip(),
            "text": content,
            "url": url,
        }
    elif "substack.com" in url:
        soup = BeautifulSoup(response.text, "lxml")
        content = str(soup.select_one(".available-content"))
        content = clean_markdown(markdownify(content))
        result = {
            "title": soup.select_one(".post-title").text.strip(),
            "text": content,
            "url": url,
        }
    elif "36kr.com" in url:
        script_content = re.findall(r"<script>window.initialState=(.*?)</script>", response.text)[0]
        encrypted_data = json.loads(script_content)
        if encrypted_data["isEncrypt"]:
            key = "efabccee-b754-4c"  # 不确定这个key是不是固定的
            decrypted_data = decrypt_aes_ecb_base64(encrypted_data["state"], key.encode("utf-8"))
        else:
            decrypted_data = encrypted_data["state"]
        decrypted_data_json = json.loads(decrypted_data)
        html_content = decrypted_data_json["articleDetail"]["articleDetailData"]["data"]["widgetContent"]
        content = clean_markdown(markdownify(html_content))
        result = {
            "title": decrypted_data_json["articleDetail"]["articleDetailData"]["data"]["widgetTitle"].strip(),
            "text": content,
            "url": url,
        }
    elif "github.com" in url:
        soup = BeautifulSoup(response.text, "lxml")
        if len(soup.select("readme-toc article")) > 0:
            content = str(soup.select_one("readme-toc article"))
        else:
            content = response.text
        content = clean_markdown(markdownify(content))
        result = {
            "title": soup.select_one("head title").text.strip(),
            "text": content,
            "url": url,
        }
    else:
        doc = Document(response.content)
        result = {
            "title": doc.title(),
            "text": markdownify(doc.summary()),
            "url": url,
        }

    return result


class MysqlTool:
    def __init__(self):
        """mysql 连接初始化"""
        self.host = config.CRAWLER_MYSQL_HOST
        self.port = config.CRAWLER_MYSQL_PORT
        self.user = config.CRAWLER_MYSQL_USER
        self.password = config.CRAWLER_MYSQL_PASSWORD
        self.db = 'novelCrawler'
        self.charset = 'utf8'
        self.mysql_conn = None

    def __enter__(self):
        """打开数据库连接"""
        self.mysql_conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.password,
            db=self.db,
            charset=self.charset
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """关闭数据库连接"""
        if self.mysql_conn:
            self.mysql_conn.close()
            self.mysql_conn = None

    def execute(self, sql: str, args: tuple = None, commit: bool = False) -> any:
        """执行 SQL 语句"""
        try:
            with self.mysql_conn.cursor() as cursor:
                cursor.execute(sql, args)
                if commit:
                    self.mysql_conn.commit()
                    logger.info(f"执行 SQL 语句：{sql}，参数：{args}，数据提交成功")
                else:
                    result = cursor.fetchall()
                    logger.info(f"执行 SQL 语句：{sql}，参数：{args}，查询到的数据为：{result}")
                    return result
        except Exception as e:
            logger.error(f"执行 SQL 语句出错：{e}")
            self.mysql_conn.rollback()
            raise e
        
def fetch_data(table_name, fields, conditions):
    """
    从指定的表中获取数据。
    
    :param table_name: 表名
    :param fields: 需要查询的字段名称列表
    :param conditions: 查询条件，应该是一个字典，其中键是列名，值是要匹配的值
    :return: 查询结果
    """
    fields_str = ', '.join(fields)

    condition_str = ' AND '.join([f"{k}='{v}'" for k, v in conditions.items()]) if conditions else '1=1'
    
    sql = f"""
        SELECT {fields_str}
        FROM {table_name}
        WHERE {condition_str}
        AND DATE(create_time) = (
            SELECT MAX(DATE(create_time))
            FROM {table_name}
            WHERE {condition_str}
        );
        """
    
    with MysqlTool() as db:
        res = db.execute(sql)
    return res



# 判断待执行的小说是否存在book_hash中
def is_book_exists(book_list, user_id, wid):
    with MysqlTool() as db:
        for book_obj in book_list:
            author = book_obj.get('作者')
            book_name = book_obj.get('小说名')
            sql = 'SELECT rid FROM book_hash WHERE author = %s AND book_name = %s AND ip = %s'
            # 执行查询
            result = db.execute(sql, (author, book_name, config.SERVER_DOMAIN))
            # 检查是否存在记录
            if result and len(result[0]) > 0:
                try:
                    rid = result[0][0]
                    logger.info(f"{book_name}-{author} 在数据库中已经存在")
                    record = WorkflowRunRecord.select().where(WorkflowRunRecord.rid==rid, WorkflowRunRecord.status=="FINISHED").first()
                    new_record = WorkflowRunRecord.create(
                        workflow_id=wid,
                        # data=record.data,
                        user_id=user_id,
                        status="FINISHED",
                        end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        # general_details=record.general_details,
                        parent_wid=wid
                    )
                    book_obj["rid"] = new_record.rid.hex

                    # 数据压缩
                    compress_workflowrunrecord(wrc_obj=new_record, data=record.data, general_details=record.general_details)
                except AttributeError as e:
                    logger.error(e)
                    continue
            else:
                continue
    logger.info(f"book_list的内容为：{book_list}")
    return book_list

