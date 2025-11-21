"""utils.py 用于处理答案和html的相关函数"""
import os
import glob
import re
import json
from urllib.parse import quote
import random
from datetime import datetime
import calendar
import pandas as pd

def read_df(file_path=None):
    """
    读取数据集，支持csv和xlsx格式。
    """
    if file_path is None:
        raise ValueError("Please specify the path of the dataframe.")
    elif file_path.endswith('xlsx'):
        return pd.read_excel(file_path)
    elif file_path.endswith('csv'):
        return pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format.")

def convert_to_search_link(text):
    """
    将文本中的特定格式文本转换为百度搜索链接。
    
    Args:
        text (str): 需要处理的文本。
    
    Returns:
        str: 处理后的文本，其中所有符合:ml-search[xxx]格式的文本将被转换为指向百度搜索结果的链接。
    
    """
    
    def replace_func(match):
        """
        将匹配到的内容替换为对应的百度搜索结果链接。
        
        Args:
            match (Match): 正则表达式匹配到的对象。
        
        Returns:
            str: 替换后的内容，格式为markdown链接。
        
        """
        # 获取[]中的内容
        keyword = match.group(1)
        # URL编码处理关键词
        encoded_keyword = quote(keyword)
        # 返回markdown格式的链接
        return f'[{keyword}](https://www.baidu.com/s?wd={encoded_keyword})'
    
    # 使用正则替换所有:ml-search[xxx]格式的文本
    result = re.sub(r':ml-search\[(.*?)\]', replace_func, text)
    return result

def get_cache_key(query, model_name, planner_version):
    """
    根据给定的参数生成缓存键。
    
    Args:
        query (str): 查询语句。
        model_name (str): 模型名称。
        planner_version (str): 规划器版本。
    
    Returns:
        str: 生成的缓存键。
    """
    cache_key = f"{model_name}_{planner_version}_{query[:40]}"
    return cache_key
    
def get_latest_cache_json(cachekey, directory="log"):
    """
    查找目录中包含 hashkey 的最新 JSON 文件并返回其内容。

    参数：
    - cachekey: 要查找的文件名中包含的关键字。
    - directory: 搜索文件的目录，默认是 "log"。

    返回：
    - 包含 JSON 数据的字典 answer_dict。如果没有找到文件，返回 None。
    """
    # 构建搜索模式，查找包含 hashkey 的 JSON 文件
    search_pattern = os.path.join(directory, f"*{cachekey}*.res.json")

    # 使用 glob 查找匹配的文件
    matching_files = glob.glob(search_pattern)

    if not matching_files:
        print("No matching files found.")
        return {}

    # 按修改时间排序，获取最新的文件
    latest_file = max(matching_files, key=os.path.getmtime)

    # 从最新文件中读取数据
    with open(latest_file, 'r', encoding='utf-8') as file:
        answer_dict = json.load(file)

    return answer_dict


def create_loading_text(normal_text, gradient_text):
    """
    生成带有加载文本的HTML代码。
    
    Args:
        normal_text (str): 常规文本内容。
        gradient_text (str): 渐变文本内容。
    
    Returns:
        str: 生成的HTML代码，包含常规文本和渐变文本的加载动画。
    
    """
    return f""" 
    <div class="status-container">
        <div class="custom-spinner"></div>  <strong>{normal_text}</strong>
        <div class="gradient-text-loading"><strong>{gradient_text}</strong></div>
    </div>
    """


def read_json_file(json_file_path):
    """
    读取指定路径的JSON文件，并返回解析后的数据。
    
    Args:
        json_file_path (str): JSON文件的路径，必须为字符串类型。
    
    Returns:
        dict: 返回一个字典对象，包含了JSON文件中的所有内容。如果读取失败，则返回None。
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def read_jsonl_file(jsonl_file_path):
    """
    读取JSON Lines格式的文件，并将其中的每一行作为独立的JSON对象进行解析。

    :param jsonl_file_path: JSON Lines文件的路径。
    :return: 返回一个列表，列表中的每一个元素都是一个JSON对象。
    """
    with open(jsonl_file_path, 'r', encoding='utf-8') as file:
        jsonl_list = [json.loads(line) for line in file]
    return jsonl_list

def save_list_as_jsonl(data_list, file_path):
    """
    将列表保存为JSON Lines格式的文件。

    :param data_list: 要保存的列表。
    :param file_path: 要保存的文件路径。
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data_list:
            # 将每个项目转换为JSON格式并写入文件，每个项目占一行
            json_line = json.dumps(item, ensure_ascii=False)
            f.write(json_line + '\n')


def generate_random_date():
    """
    生成随机的日期字符串，格式为“YYYY年MM月DD日”，年份在2018-2025年之间。

    :return: 随机日期的字符串表示形式。
    """
    
    # 生成随机年份
    year = random.randint(2018, 2025)
    
    # 生成随机月份
    month = random.randint(1, 12)
    
    # 获取当前月份的天数
    days_in_month = calendar.monthrange(year, month)[1]
    
    # 生成随机日
    day = random.randint(1, days_in_month)
    
    # 格式化输出
    date_str = f"{year}年{month}月{day}日"
    return date_str


def is_changed(row):
    """
    判断是否为变更的工具，如果有变更的工具，则返回True，否则返回False
    """
    t=eval(row["select_tools"])
    try:
        for i in t:
            if name2srcid[i] in changed_srcid:
                return True
    except KeyError:
        return False

    return False


def get_str_before(str_full, before_this):
    """
    从完整字符串中提取出指定字符串之前的全部内容。

    :param str_full: 完整的字符串
    :param before_this: 用于定位的字符串，提取其之前的内容
    :return: before_this 之前的全部字符串
    """
    # 使用正则表达式搜索 before_this 在 str_full 中的位置
    match = re.search(re.escape(before_this), str_full)
    if match:
        # 如果找到 before_this，返回其之前的全部字符串
        return str_full[:match.start()]
    else:
        # 如果 before_this 不在 str_full 中，返回空字符串或完整字符串
        return str_full
