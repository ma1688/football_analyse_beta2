# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :asia_eu_data.py
# @Time      :2024/7/22 下午5:35
# @Author    :MA-X-J
# @Software  :PyCharm
import asyncio
import json
import os
import random
import re
import time
from datetime import datetime

import chardet
import httpx
import pandas as pd
from colorama import Fore, Style
from lxml import html
from parsel import Selector

from logger import logger

base_url = "https://odds.500.com/fenxi/"
current_date = datetime.now().strftime("%Y-%m-%d")
formatted_now = datetime.now().strftime("%Y-%m-%d %H:%M")
pan_dict = {'威廉希尔': '293', '澳门': '5', 'Bet365': '3', 'Interwetten': '4', '皇冠': '280',
            '易胜博': '9', '伟德': '6', 'Bwin': '11', }


async def get_random_user_agent():
    """随机获取user_agent"""
    USER_AGENT_LIST = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 "
        "Safari/537.36 Edge/16.16299",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 "
        "Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 "
        "Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 "
        "Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 "
        "Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 "
        "Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 "
        "Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 "
        "Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 "
        "Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 "
        "Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 "
        "Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 "
        "Safari/537.36",
    ]
    return random.choice(USER_AGENT_LIST)  # 返回随机的User-Agent


async def get_headers():
    return {
        "Host": "odds.500.com",
        "User-Agent": await get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,"
                  "image/svg+xml,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": f"WT_FPC=id=undefined:lv={int(time.time()*1000)}:ss={int(time.time()*1000)}",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Priority": "u=4",
        "TE": "trailers",
        "Referer": "https://live.500.com/",
    }


async def first_req(data_type, fid_value):
    """基础req
    获取url
    :param data_type: 欧指 亚陪  ouzhi,yazhi
    :param fid_value: 比赛id
    :return: 返回数据
    """
    url_params = f"{data_type}-{fid_value}.shtml"

    response = httpx.get(url=base_url + url_params, headers=await get_headers(),
                         verify=False, timeout=5.688)
    content = response.content
    # 检测编码格式
    result = chardet.detect(content)

    encoding = result['encoding']
    # 解码HTML代码片段
    html_content = content.decode(encoding, 'ignore')

    return Selector(text=html_content)


async def second_req(semaphore, url_params, url_name):
    """
    二次请求详细数据
    :param semaphore: 异步任务数量
    :param url_params: 请求完整的url
    :param url_name: 用于标识请求的名称
    :return: 包含标识信息和请求结果的字典
    """
    try:
        async with semaphore:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=url_params,
                    headers=await get_headers(),
                    # headers=he,
                    timeout=16.688
                )
                response.raise_for_status()
                if response.status_code == 200:
                    return {"name": url_name, "data": json.loads(response.text)}
                else:
                    return {"name": url_name, "data": None}
    except Exception as e:
        logger.error(f"二次请求出错: {e}")
        return {"name": url_name, "data": None}


async def get_europe_url(fid):
    """获取欧赔初盘同赔url"""
    resp = await first_req("ouzhi", fid)
    url_name = resp.xpath('//tr/td[2]/p/a/span[@class="quancheng"]/text()').getall()
    url_list = resp.xpath('//tr/td[7]/a[3]/@href').getall()
    url_dict = dict(zip(url_name, url_list))
    # Filter url_dict to only include keys that are present in pan_dict
    filtered_url_dict = {key: url_dict[key] for key in url_dict if key in pan_dict}
    new_url_dict = {}
    for key, value in filtered_url_dict.items():
        pattern = r".*cid=(\d+)&win=([\d.]+)&draw=([\d.]+)&lost=([\d.]+).*"
        # Search for the pattern in the URL string
        match = re.search(pattern, value)
        if match:
            # Extracting the values
            cid = match.group(1)
            win = match.group(2)
            draw = match.group(3)
            lost = match.group(4)
            new_url_dict[
                key] = f"https://odds.500.com/fenxi1/inc/ouzhi_sameajax.php?cid={cid}&win={win}&draw={draw}&lost={lost}&id={fid}&mid=0"
        else:
            logger.info("No match found")
    return new_url_dict


async def convert_to_datetime(a):
    year = datetime.now().year
    date_time_str = str(year) + '-' + a + ':00'

    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    return date_time_obj


async def get_asia_url(fid, vs_date):
    """获取亚赔初盘同赔url"""
    # 对vsdate处理
    new_vs_date = await convert_to_datetime(vs_date)
    # 1. 获取各家亚赔公司的url
    resp = await first_req(f"yazhi", fid)
    url_name = resp.xpath('//tr/td[2]/p/a/span[@class="quancheng"]/text()').getall()  # 公司名称
    url_list = resp.xpath('//tr/td[7]/a[3]/@href').getall()  # 公司url

    url_dict = dict(zip(url_name, url_list))
    # Filter url_dict to only include keys that are present in pan_dict
    filtered_url_dict = {key: url_dict[key] for key in url_dict if key in pan_dict}
    new_url_dict = {}
    for key, value in filtered_url_dict.items():
        pattern = r"cid=(\d+)&cp=([^&]+)&.*s1=([0-9.]+)&s2=([0-9.]+)"

        match = re.search(pattern, value)
        if match:
            cid, cp, s1, s2 = match.groups()
            new_url = f"https://odds.500.com/fenxi1/inc/yazhi_sameajax.php?cid={cid}&cp={cp}&s1={s1}&s2={s2}&id={fid}&mid=0&vsdate={new_vs_date}&t={int(time.time() * 1000)}"
            new_url_dict[key] = new_url
            # aa = await second_req(asyncio.Semaphore(5), new_url, key)
            # await process_asia_data(aa["data"])
            # if len(new_url_dict) == 1:
            #     break
        else:
            logger.info("No match found")
    return new_url_dict


async def get_eu_asia(choose_list: list):
    """
    主函数
    :param choose_list: 选择的比赛ID
    :return:
    """
    for match_data in choose_list:
        fid_value = match_data.get('fid', None)
        cnum = match_data.get('场次', None)
        Events = match_data.get('赛事', None)
        Rounds = match_data.get('轮次', None)
        matches_time = match_data.get('比赛时间', None)
        state = match_data.get('状态', None)
        home_name = match_data.get('主队', None)
        away_name = match_data.get('客队', None)
        score = match_data.get('比分', None)
        rq = match_data.get('让球', None)
        await main(fid_value, Events, Rounds, home_name, matches_time)


async def process_eu_data(company_name, eu_data):
    """
    处理欧盘数据
    :return:
    """
    new_eu_data = []
    count = eu_data['counts']
    if count == [0, 0, 0]:
        logger.info(f"该公司无数据")
        return False
    else:
        row = eu_data['row']
        match = eu_data['match']
        for i_value in range(len(row)):
            row_data = {"欧盘公司": company_name, "f_id": row[i_value][4],
                        "赛事": match[str(row[i_value][0])].replace("\u3000\u3000", "").strip(),
                        "比赛日期": row[i_value][3],
                        "主队": row[i_value][5], "客队": row[i_value][8],
                        "比分": str(row[i_value][6]) + ":" + str(row[i_value][7]),
                        "终赔": [row[i_value][10], row[i_value][11], row[i_value][12]]}

            new_eu_data.append(row_data)

        return new_eu_data


async def process_asia_data(company_name, asia_data):
    """
    处理亚盘数据

    :param company_name:
    :param asia_data:
    :return:
    """
    row = asia_data['row']  # 同盘比赛信息
    match = asia_data['match']  # 联赛类型
    if match is None:
        logger.info("该公司无数据")
        return False
    else:
        new_asia_data = []
        for s1 in row:
            tree = html.fromstring(s1)
            league1 = tree.xpath('//a[contains(@href, "https://liansai.500.com/zuqiu-")]/text()')[0].replace(
                "\u3000\u3000", "").strip()
            date1 = tree.xpath('//td[2]/text()')[0]
            match1 = tree.xpath('//td[@class="dz"]/a/text()')[0].replace('\xa0', ' ')
            parts = match1.split("  ")

            home_team = parts[0]  # 主队名称
            score = parts[1]  # 比分
            away_team = parts[2]  # 客队名称
            result1 = tree.xpath('//td/span/text()')[0]
            odds1 = tree.xpath('//td[position() > 7 and position() < 16]/text()')
            row_data = {"欧盘公司": company_name, "联赛": league1, "日期": date1, "主队": home_team, "比分": score,
                        "客队": away_team,
                        "结果": result1,
                        "赔率": odds1}
            new_asia_data.append(row_data)
        return new_asia_data


async def main(fid_value, Events, Rounds, home_name, vs_date):
    """
    Main function to create and run tasks for fetching data from URLs in filtered_url_dict.
    """
    new_eu_url_dict = await get_europe_url(fid_value)
    new_asia_url_dict = await get_asia_url(fid_value, vs_date)

    eu_tasks = []
    asia_tasks = []

    semaphore = asyncio.Semaphore(2)  # 最多允许5个并发任务
    # 在创建任务时，传递额外的标识信息
    for url_name, url in new_eu_url_dict.items():
        eu_tasks.append(second_req(semaphore, url, url_name))

    for url_name, url in new_asia_url_dict.items():
        asia_tasks.append(second_req(semaphore, url, url_name))

    # 处理结果时，可以通过标识信息区分每个任务的返回值
    eu_results = await asyncio.gather(*eu_tasks, return_exceptions=True)
    await asyncio.sleep(5, 10)
    asia_results = await asyncio.gather(*asia_tasks, return_exceptions=True)

    eu_data = []
    asia_data = []
    for result in eu_results:
        # logger.info(f"URL Name: {result['name']}, Data: {result['data']}")
        if result['data'] is not None:
            if result['data']['counts'] == [0, 0, 0]:
                logger.info(f"{Fore.RED}{result['name']}欧赔同盘数据为空{Style.RESET_ALL}")
                time.sleep(1.6888)
            else:
                eu_list = await process_eu_data(result['name'], result['data'])
                eu_data += eu_list

    data_directory = f'./data/eu_odds/{Events}/{Rounds}'
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    eu_list = pd.DataFrame(eu_data)
    eu_list.to_csv(f"./data/eu_odds/{Events}/{Rounds}/{home_name}_eu_results.csv", index=False)

    for result in asia_results:
        # logger.info(f"URL Name: {result['name']}, Data: {result['data']}")
        if result['data'] is not None:
            if result['data']['match'] is None:
                logger.info(f"{Fore.RED}{result['name']}亚赔同盘数据为空{Style.RESET_ALL}")
                time.sleep(1.6888)
            else:
                asia_list = await process_asia_data(result['name'], result['data'])
                asia_data += asia_list

    data_directory = f'./data/asia_odds/{Events}/{Rounds}'
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    asia_list = pd.DataFrame(asia_data)
    asia_list.to_csv(f"./data/asia_odds/{Events}/{Rounds}/{home_name}_asia_results.csv", index=False)

    logger.info(f"{Fore.GREEN}欧亚赔数据处理完成{Style.RESET_ALL}")


# Run the main function
if __name__ == "__main__":
    t = time.time()
    # logger.info(int(time.time() * 1000))
    # asyncio.run(get_eu_asia())
    asyncio.run(get_asia_url(1145346, "07-23 00:00"))
    logger.info(f"Time taken: {time.time() - t} seconds.")
