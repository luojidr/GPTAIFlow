# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-04-13 15:45:13
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-07-21 18:26:50
from urllib.parse import urlparse, parse_qs

import requests
#import yt_dlp
import pandas as pd
from utilities.workflow import Workflow
from utilities.web_crawler import MysqlTool, crawl_text_from_url, fetch_data, is_book_exists, proxies
from worker.tasks import task
import threading
from utilities.print_utils import logger
import re
import uuid
from lxml import etree
pattern = re.compile('\n([\d]+)\n')


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}
lock = threading.Lock()


def get_aid_cid(bvid, part_number):
    table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
    tr = {}
    for i in range(58):
        tr[table[i]] = i
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608

    if "BV" in bvid:
        r = 0
        for i in range(6):
            r += tr[bvid[s[i]]] * 58**i
        aid = (r - add) ^ xor
    else:
        aid = bvid

    url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp"
    resp = httpx.get(url, headers=headers, proxies=proxies())
    info = resp.json()
    cid = info["data"][part_number - 1]["cid"]

    return aid, cid


@task
def text_crawler(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    input_url = workflow.get_node_field_value(node_id, "url")
    if input_url is None or (isinstance(input_url, str) and input_url == ""):
        raise Exception("url is empty")
    if isinstance(input_url, str):
        urls = [input_url]
    elif isinstance(input_url, list):
        urls = input_url

    output_type = workflow.get_node_field_value(node_id, "output_type")
    output_data = {
        "text": [],
        "title": [],
    }
    for url in urls:
        result = crawl_text_from_url(url)
        if output_type == "text":
            output_data["text"].append(result["text"])
            output_data["title"].append(result["title"])
        elif output_type == "json":
            output_data["text"].append(result)

    if output_type == "text":
        text_value = output_data["text"] if isinstance(input_url, list) else output_data["text"][0]
        title_value = output_data["title"] if isinstance(input_url, list) else output_data["title"][0]
        workflow.update_node_field_value(node_id, "output_text", text_value)
        workflow.update_node_field_value(node_id, "output_title", title_value)
    elif output_type == "json":
        text_value = output_data["text"] if isinstance(input_url, list) else output_data["text"][0]
        workflow.update_node_field_value(node_id, "output_text", text_value)
    return workflow.data


@task
def bilibili_crawler(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    url_or_bvid = workflow.get_node_field_value(node_id, "url_or_bvid")
    output_type = workflow.get_node_field_value(node_id, "output_type")

    if "b23.tv" in url_or_bvid:
        resp = requests.get(url_or_bvid, headers=headers, proxies=proxies(), follow_redirects=True)
        url_or_bvid = f"{resp.url.scheme}://{resp.url.host}{resp.url.path}"

    if "bilibili.com" in url_or_bvid:
        if not url_or_bvid.startswith("http"):
            url_or_bvid = "https://" + url_or_bvid
        parsed_url = urlparse(url_or_bvid)
        path_components = parsed_url.path.split("/")
        bvid = path_components[2].split("?")[0]
        query_dict = parse_qs(parsed_url.query)
        part_number = int(query_dict.get("p", ["1"])[0])
    else:
        bvid = url_or_bvid
        part_number = 1

    aid, cid = get_aid_cid(bvid, part_number=part_number)
    resp = requests.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers=headers, proxies=proxies())
    title = resp.json()["data"]["title"]

    resp = requests.get(f"https://api.bilibili.com/x/player/wbi/v2?aid={aid}&cid={cid}", headers=headers, proxies=proxies())
    subtitle_list = resp.json()["data"]["subtitle"]["subtitles"]
    if len(subtitle_list) == 0:
        subtitle_data = [] if output_type == "list" else ""
    else:
        # TODO: 这里直接选择列表第一个作为字幕了，对于多语言字幕未来要考虑让用户选择语言？
        subtitle_url = subtitle_list[0]["subtitle_url"]
        if subtitle_url.startswith("//"):
            subtitle_url = "https:" + subtitle_url
        subtitle_resp = requests.get(subtitle_url, headers=headers)
        subtitle_data_list = subtitle_resp.json()["body"]
        subtitle_data_list = [item["content"] for item in subtitle_data_list]
        subtitle_data = "\n".join(subtitle_data_list) if output_type == "str" else subtitle_data_list

    workflow.update_node_field_value(node_id, "output_subtitle", subtitle_data)
    workflow.update_node_field_value(node_id, "output_title", title)
    return workflow.data


@task
def youtube_crawler(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    url_or_video_id = workflow.get_node_field_value(node_id, "url_or_video_id")
    output_type = workflow.get_node_field_value(node_id, "output_type")

    if isinstance(url_or_video_id, list):
        urls = url_or_video_id
    else:
        urls = [url_or_video_id]

    formatted_urls = []
    for url in urls:
        if "youtube.com" in url:
            if not url.startswith("http"):
                url = "https://" + url
        elif "youtu.be" in url:
            if not url.startswith("http"):
                url = "https://" + url
        else:
            url = "https://www.youtube.com/watch?v=" + url
        formatted_urls.append(url)

    text_results = []
    title_results = []
    for url in formatted_urls:
        ydl_opts = {"writeautomaticsub": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info["title"]

        # TODO: 这里直接选择列表第一个作为字幕了，对于多语言字幕未来要考虑让用户选择语言？
        if len(info["subtitles"]) > 0:
            subtitle_key = list(info["subtitles"].keys())[0]
            subtitle_file_list = info["subtitles"][subtitle_key]
            for subtitle_file in subtitle_file_list:
                if subtitle_file["ext"] == "json3":
                    subtitle_url = subtitle_file["url"]
                    break
        elif len(info["automatic_captions"]) > 0:
            for caption_key in info["automatic_captions"]:
                if not caption_key.startswith("en"):
                    continue
                caption_file_list = info["automatic_captions"][caption_key]
                for caption_file in caption_file_list:
                    if caption_file["ext"] == "json3":
                        subtitle_url = caption_file["url"]
                        break
                break
        else:
            raise Exception("No subtitle found")

        subtitle_resp = requests.get(subtitle_url, proxies=proxies(), headers=headers)
        subtitle_data_list = subtitle_resp.json()["events"]
        formated_subtitle = []
        for item in subtitle_data_list:
            if "segs" not in item:
                continue
            line = "".join([seg["utf8"] for seg in item["segs"]]).strip()
            if len(line) == 0:
                continue
            formated_subtitle.append(line)
        subtitle_data = "\n".join(formated_subtitle) if output_type == "str" else formated_subtitle

        text_results.append(subtitle_data)
        title_results.append(title)

    title_value = title_results if isinstance(url_or_video_id, list) else title_results[0]
    workflow.update_node_field_value(node_id, "output_title", title_value)
    text_value = text_results if isinstance(url_or_video_id, list) else text_results[0]
    workflow.update_node_field_value(node_id, "output_subtitle", text_value)
    return workflow.data

import asyncio

@task
def tvmao_crawler(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    series_name = workflow.get_node_field_value(node_id, "series_name")
    with lock:
        output_episodes, output_info = asyncio.run(asynv_crawler(series_name))

    workflow.update_node_field_value(node_id, "output_episodes", output_episodes)
    workflow.update_node_field_value(node_id, "output_info", output_info)
    return workflow.data


async def asynv_crawler(series_name) -> None:
    from playwright.async_api import Playwright, async_playwright, expect, TimeoutError
    output_info = ""
    output_episodes = ""
    episodes = []
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless = True)
        browser_context = await browser.new_context()

        page = await browser_context.new_page()
        await page.goto("https://www.tvmao.com/", timeout=600000)
        await page.get_by_role("textbox", name="节目、电视剧、电影、明星一起搜！").click()
        await page.get_by_role("textbox", name="节目、电视剧、电影、明星一起搜！").fill(series_name)
        await page.get_by_role("textbox", name="节目、电视剧、电影、明星一起搜！").press("Enter")
        try:
            await page.get_by_role("link", name=series_name+"剧情介绍").first.click()
        except TimeoutError:
            raise Exception("暂未找到相关电视剧信息")
        try:
            await page.get_by_role("link", name="分集剧情").click()
        except TimeoutError:
            raise Exception("暂无相关剧集信息")
        await page.wait_for_load_state(timeout=600000)
        e_pattern = re.compile(r'(/drama/[^/]+/episode(?:/[\d\-]+)?)')
        matches = e_pattern.findall(await page.content())
        for match in list(set(matches)):
            episodes.append(f'https://www.tvmao.com{match}')
            episodes.sort()
        info_1 = await page.locator("xpath=//html/body/div[2]/div/div[1]/div/p[1]").all_text_contents()
        info_2 = await page.locator("xpath=//html/body/div[2]/div/div[1]/div/p[2]").all_text_contents()
        output_episodes += replace_multiple_spaces(info_1[0].replace("\n", "")) + "\n"
        output_episodes += replace_multiple_spaces(info_2[0].replace("\n", ""))
    for url in episodes:
        res = requests.get(url, headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
        html_content = res.content.decode('utf-8')
        html_tree = etree.HTML(html_content)
        title = html_tree.xpath("//html/body/div[3]/div/div[1]/p")[0].text
        output_info += "## " + str(title).strip().replace("\n", "") + "\n"
        contents = html_tree.xpath("//html/body/div[3]/div/div[1]/article/p")
        content = ("").join([content.text for content in contents])
        output_info += content + "\n"
    return output_info, output_episodes

def replace_multiple_spaces(text):
    return ' '.join(text.split())


@task
def fanqie_crawler(
    workflow_data: dict,
    node_id: str,):
    workflow = Workflow(workflow_data)
    rankOptions = workflow.get_node_field_value(node_id, "rankOptions")
    qdSexOptions = workflow.get_node_field_value(node_id, "qdSexOptions")
    dbListType = workflow.get_node_field_value(node_id, "dbListType")
    prompt = workflow.get_node_field_value(node_id, "prompt")
    user_id = workflow_data['user_id']
    wid = workflow.workflow_id
    path = f"tmp_data/{uuid.uuid4()}book_rankings.xlsx"
    res = []
    book_rankings_res = []
    conditions = {}
    logger.info(f"rankOptions: {rankOptions}")
    logger.info(f"qdSexOptions: {qdSexOptions}")
    logger.info(f"dbListType: {dbListType}")
    logger.info(f"prompt: {prompt}")
    if rankOptions:
        if len(rankOptions) == 1:
            fields = ["author", "book_name", "category", "rank_score"]
            res = fetch_data(table_name="fq_pinnacle_book", fields=fields, conditions={})
            book_rankings_res = [
                    {
                        "作者": result[0],
                        "小说名": result[1],
                        "题材与类型": result[2],
                        "巅峰值": result[3],
                    }
                    for result in res
                ]
        else:
            fields = ["author", "book_name", "category", "list_type"]
            if rankOptions[0] == "男频排行榜":
                conditions["list_type"] = rankOptions[2]
                conditions["category"] = rankOptions[1]
                conditions["sex"] = "male"
            else:
                conditions["list_type"] = rankOptions[2]
                conditions["category"] = rankOptions[1]
                conditions["sex"] = "female"
            res = fetch_data(table_name="fq_ranking_book", fields=fields, conditions=conditions)
            book_rankings_res.extend([
                {
                        "作者": result[0],
                        "小说名": result[1],
                        "题材与类型": result[2],
                        "榜单类型": result[3],
                }
                for result in res
            ])
            
    elif qdSexOptions:
        fields = ["author", "book_name", "book_genre", "list_type"]
        if qdSexOptions[0] == "男频排行榜":
            conditions["genre"] = qdSexOptions[2]
            conditions["list_type"] = qdSexOptions[1]
            conditions["sex"] = "male"
        else:
            conditions["genre"] = qdSexOptions[2]
            conditions["list_type"] = qdSexOptions[1]
            conditions["sex"] = "female"
        res = fetch_data(table_name="qd_ranking_book", fields=fields, conditions=conditions)
        book_rankings_res.extend([
            {
                    "作者": result[0],
                    "小说名": result[1],
                    "题材与类型": result[2],
                    "榜单类型": result[3],
            }
            for result in res
        ])
    elif dbListType:
        conditions["ranking_type"] = dbListType[0]
        if len(dbListType) == 2:
            if dbListType[0] != "原创":
                list_type = f"{dbListType[0]}・{dbListType[1]}"
            else:
                list_type = dbListType[1]
            conditions["list_type"] = list_type
        else:
            if dbListType[0] != "原创":
                list_type = f"{dbListType[0]}・{dbListType[1]}（{dbListType[2][0]}）"
            else:
                list_type = f"{dbListType[1]}（{dbListType[2][0]}）"
            conditions["list_type"] = list_type
        fields = ["author", "book_name", "book_genre", "list_type"]
        logger.info(f"conditions:  {conditions}")
        res = fetch_data(table_name="db_ranking_book", fields=fields, conditions=conditions)
        book_rankings_res.extend([
            {
                    "作者": result[0],
                    "小说名": result[1],
                    "题材与类型": result[2],
                    "榜单类型": result[3],
            }
            for result in res
        ])
    logger.info(f"book_rankings_res{book_rankings_res}")
    book_rankings_res = is_book_exists(book_rankings_res, user_id, wid)
    if book_rankings_res:
        df = pd.DataFrame(book_rankings_res)
        if len(rankOptions) == 1:
            df.drop(['巅峰值'], axis=1, inplace=True)
        else:
            df.drop(['榜单类型'], axis=1, inplace=True)
        df.to_excel(path, index=False)
        book_rankings_res = [{k: v for k, v in book_item.items() if k != 'rid'} for book_item in book_rankings_res]
    workflow.update_node_field_value(node_id, "output", [path])
    workflow.update_node_field_value(node_id, "origin_content_output", book_rankings_res)
            
    return workflow.data




