# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :match_live.py
# @Time      :2024/6/28 上午11:22
# @Author    :MA-X-J
# @Software  :PyCharm
import logging
import re
from datetime import datetime

import chardet
import httpx
import pymysql
from parsel import Selector
from prettytable import PrettyTable

from base_data import main_base_data

# 创建一个logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # 设置logger的级别为INFO

# 创建一个handler，用于写入日志文件
fh = logging.FileHandler('./match_live.log')
fh.setLevel(logging.ERROR)  # 设置handler级别为ERROR
ch = logging.FileHandler('./matches.log')
ch.setLevel(logging.INFO)  # 设置handler级别为INFO

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)  # 为文件handler设置格式
ch.setFormatter(formatter)  # 为控制台handler设置格式

# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)

# 设置基础配置的日志级别为ERROR
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def insert_match_data_to_db(match_data):
    DB_HOST = "1.14.239.79"
    DB_PORT = 3306
    DB_USER = "zq_data"
    DB_PASSWORD = "zq_data1688"
    DB_NAME = "zq_data"

    connection = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, db=DB_NAME,
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS `赛事列表` (
                `fid` VARCHAR(255),
                `场次` INT,
                `赛事` VARCHAR(255),
                `轮次` VARCHAR(255),
                `比赛时间` DATETIME,
                `状态` VARCHAR(255) NOT NULL,
                `主队` VARCHAR(255),
                `比分` VARCHAR(255),
                `客队` VARCHAR(255),
                `让球` VARCHAR(255) NOT NULL,
                PRIMARY KEY (`fid`)
            ) CHARSET=utf8mb4;
            """
            cursor.execute(create_table_query)

            insert_query = """
            INSERT INTO `赛事列表` (`fid`, `场次`, `赛事`, `轮次`, `比赛时间`, `状态`, `主队`, `比分`, `客队`, `让球`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                `场次` = VALUES(`场次`),
                `赛事` = VALUES(`赛事`),
                `轮次` = VALUES(`轮次`),
                `比赛时间` = VALUES(`比赛时间`),
                `状态` = VALUES(`状态`),
                `主队` = VALUES(`主队`),
                `比分` = VALUES(`比分`),
                `客队` = VALUES(`客队`),
                `让球` = VALUES(`让球`);
            """

            current_year = datetime.now().year
            for match in match_data:
                match_datetime = f"{current_year}-{match['比赛时间']}:00"  # Adding seconds part as '00'
                match_status = match['状态'] if match['状态'] else "正在进行"  # Replace null or empty '状态' with "正在进行"
                let_ball = match['让球'] if match['让球'] else "0"  # Replace null or empty '让球' with "0"
                cursor.execute(insert_query, (
                    match['fid'], match['场次'], match['赛事'], match['轮次'], match_datetime, match_status,
                    match['主队'], match['比分'], match['客队'], let_ball))

            connection.commit()

    finally:
        connection.close()


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
            if all(value is None for value in data.values()):
                continue
            parse_data.append(data)

        table = PrettyTable()
        if parse_data:
            table.field_names = list(parse_data[0].keys())

        for data in parse_data:
            if data['状态'] == '完':
                # Wrap each value in red ANSI escape codes
                red_row = [f"\033[91m{value}\033[0m" for value in data.values()]
                table.add_row(red_row)
            else:
                table.add_row(list(data.values()))
        print(table)
        return parse_data

    except Exception as e:
        logger.error(f"Error occurred while parsing HTML content: {e}")
        return None


if __name__ == '__main__':
    html = get_zqdc()
    selector = parse_html_content(html)
    while True:
        if selector:
            while True:
                chose_list = []
                match_list = select_data(selector)
                # insert_match_data_to_db(match_list)
                choose = input(f"请选择你想要的比赛场次范围(例如:1-8或1): ")
                try:
                    # 输入'++'退出
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
                                logger.info(match)
                                chose_list.append(match)
                except ValueError:
                    logger.error(
                        "输入的场次范围不正确，请重新输入。")
                # print(chose_list)
                main_base_data(chose_list)
        else:
            logger.error("Selector is None.")
            break
