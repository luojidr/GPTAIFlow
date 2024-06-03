import pandas as pd
from utilities.print_utils import logger


def sheets_parse(files: list[str]):
    tag_list = []
    content_list = []
    # 表格解析直接洗表格文件
    excel_file_suffixs = ("xls", "csv", "xlsx", "xlsm")
    for file in files:
        if not file.endswith(excel_file_suffixs):
            continue
        data = pd.read_excel(io=file, sheet_name=None)
        user_name = file.split("/")[1]
        for sheet_name, df in data.items():
            df.fillna("", inplace=True)
            logger.info(f"sheet_name {sheet_name}")
            tag_list.extend(df.columns.tolist())
            sheet_content = list(df.values)
            if sheet_content:
                for rows in sheet_content:
                    content_dict = {
                        k: get_sheet_file_path(str(v), user_name) for k, v in zip(tag_list, rows)
                    }
                    content_list.append(content_dict)
    return content_list


def get_sheet_file_path(value: str, user_name: str) -> str:
    """解析excel中的单元格文件路径. ,返回完整文件路径.
    支持的文件有: txt, md, html, json, csv, docx, xlsx, pptx, pdf
    Args:
        value (str): 待解析的单元格内容
        user_name (str): 用户user_name 的hash值
    Returns:
        str: 完整的文件路径
    """
    
    filesuffix = (".txt", ".md", ".html", ".json", ".csv", ".docx", ".xlsx", ".pptx", ".pdf")
    if value.endswith(filesuffix):
        if not value.startswith("tmp_data/"):
            value = [f"tmp_data/{user_name}/" + value]
    return value
