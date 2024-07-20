# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :match_live.py
# @Time      :2024/6/28 上午11:22
# @Author    :MA-X-J
# @Software  :PyCharm
import logging
import re

import chardet
import httpx
from parsel import Selector
from prettytable import PrettyTable

# 创建一个logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 创建一个handler，用于写入日志文件
fh = logging.FileHandler('./match_live.log')
fh.setLevel(logging.DEBUG)

# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def parse_html(text):
    patterns = {
        'fid': r'fid="(\d+)"',
        '场次': r'<td align="center" class=""><input type="checkbox" name="check_id\[\]" value="\d+">(\d+)</td>',
        '赛事': r'class="ssbox_01"><a .*?>(.*?)</a></td>',
        '轮次': r'<td align="center">(.*?)</td>',
        '比赛时间': r'<td align="center">(\d{2}-\d{2} \d{2}:\d{2})</td>',
        '状态': r'<span class="red">(.*?)<\/span>|<td align="center">(未)<\/td>|<td align="center" class="td_living">('
                r'\d+)<\/td>',
        '主队': r'<td align="right" class="p_lr01">.*?<a[^>]*>([^<]*)</a>',
        '比分': r'<td align="center" class="red">\s*(.*?)\s*</td>',
        '客队': r'<td align="left" class="p_lr01"><a[^>]*>([^<]*)</a>',
        '让球': r'class="sp_rq">\((.*?)\)'
    }

    # Extract the data
    extracted_data = {}
    for key, pattern in patterns.items():
        try:
            match = re.search(pattern, text)
            if match:
                if key == '状态':
                    # 处理 '状态' 键的多个捕获组，确保匹配到某个组的内容
                    extracted_data[key] = next((group for group in match.groups() if group), None)
                else:
                    extracted_data[key] = match.group(1)
            else:
                extracted_data[key] = None
        except IndexError as e:
            logger.error(f"Error occurred while parsing HTML content for key '{key}': {e}")
            extracted_data[key] = None

    # print(extracted_data)
    return extracted_data


# 请求数据
def get_zqdc(e=24074):
    """
    获取足球单场
    :return:
    """
    url = 'https://live.500.com/zqdc.php?e={}'.format(e)
    headers = {
        "Host": "live.500.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://live.500.com/zqdc.php",
        "Connection": "keep-alive",
        "Cookie": "ck_RegFromUrl=https%3A//odds.54fined:lv=171954528erflag=1::3; CLI61310106.45076::B8ED2705E86B4D811FE",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0, i",
        "TE": "trailers"
    }

    try:
        resp = httpx.get(url, headers=headers, timeout=10, verify=False)
        if resp.status_code == 200:
            return resp.content
        else:
            return None
    except Exception as e:
        logger.error(e)
        return None


# 生成选择器
def parse_html_content(html_data):
    try:
        resp = html_data
        encoding = chardet.detect(resp)['encoding']
        html_content = resp.decode(encoding, 'ignore')
        selector_xpath = Selector(text=html_content)
        return selector_xpath
    except Exception as e:
        logger.error(f"Error occurred while parsing HTML content: {e}")
        return None


def select_data(selector):
    try:
        match_data_xpath = selector.xpath("//tbody/tr").getall()
        parse_data = []
        for match in match_data_xpath:
            data = parse_html(match)
            # Skip adding the data to parse_data if all values are None
            if all(value is None for value in data.values()):
                continue
            parse_data.append(data)

        # Create a prettytable object
        table = PrettyTable()
        # Set the field names to the keys of the first dictionary in parse_data
        table.field_names = list(parse_data[0].keys()) if parse_data else []

        # Add a row for each dictionary in parse_data
        for data in parse_data:
            table.add_row(list(data.values()))

        # Print the table
        print(table)

        return parse_data

    except Exception as e:
        logger.error(f"Error occurred while parsing HTML content: {e}")
        return None


if __name__ == '__main__':
    html = get_zqdc()
    # print(html)
    selector = parse_html_content(html)
    chose_list = []
    while True:
        if selector:
            match_list = select_data(selector)
            try:
                choose = input(f"请选择你想要的比赛场次范围(例如:1-8或1): ")
                if choose == '++':
                    break
                if ',' in choose:
                    start_match, end_match = choose.split(',')
                else:
                    start_match = end_match = choose
                # 检查"场次"列是否在你想要的范围内
                if start_match and end_match:
                    start_num = int(start_match)
                    end_num = int(end_match)
                    for match in match_list:
                        if start_num <= int(match['场次']) <= end_num:
                            print(match)
                            chose_list.append(match)
            except ValueError:
                print("输入的场次范围不正确，请重新输入。")

        else:
            logger.error("Selector is None.")
            break
