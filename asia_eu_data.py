# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :asia_eu_data.py
# @Time      :2024/7/22 下午5:35
# @Author    :MA-X-J
# @Software  :PyCharm
import asyncio
import json
import logging
import os
import random
import re
import time
from datetime import datetime

import chardet
import httpx
import pandas as pd
from parsel import Selector

# 创建一个logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # 设置logger的级别为INFO

# 创建一个handler，用于写入日志文件
log_directory = f'./data/log/'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
# 创建一个handler，用于写入日志文件
fh = logging.FileHandler(f'{log_directory}asia_eu_data.log')
fh.setLevel(logging.ERROR)  # 设置handler级别为ERROR

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)  # 为文件handler设置格式

# 给logger添加handler
logger.addHandler(fh)

# 设置基础配置的日志级别为ERROR
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
        "Cookie": "WT_FPC=id=undefined:lv=1721568321596:ss=1721568321596; "
                  "ck_RegFromUrl=https%3A//www.baidu.com/link%3Furl"
                  "%3DLP86gRTLBgxW_wOoE2V5pJMmvY3MJsJKu29lHjEcGAXgTTOj98hJjnq41gwD7mDk%26wd%3D%26eqid"
                  "%3De1a103a50003858b0000000664f046e4; isautologin=1; isagree=1; "
                  "Hm_lvt_4f816d475bb0b9ed640ae412d6b42cab=1719823600; "
                  "_jzqa=1.699021464142686100.1719823602.1719823602.1719826778.2; "
                  "_qzja=1.807376057.1719823601650.1719823601650.1719826778157.1719824728776.1719826778157.0.0.0.13.2"
                  "; __utma=63332592.1917194613.1719823603.1719823603.1719823603.1; "
                  "__utmz=63332592.1719823603.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); "
                  "_jzqx=1.1719826778.1719826778.1.jzqsr=odds%2E500%2Ecom|jzqct=/fenxi1/yazhi_same%2Ephp.-; "
                  "ck_regchanel=_ad0.7232252524252528; regfrom=0%7Cala%7Cbaidu; ck_RegUrl=odds.500.com; "
                  "pcTouchDownload500App=op_chupan; "
                  "ck=MjAyMzA4MTgwMDAwNTUzOTA1ZmM3MTcwODAzMTBjYWI2MDZiMWIwMTIyNjdiYmZh; sdc_session=1692587441720; "
                  "motion_id=1719824728136_0.8512543739505686; Hm_lpvt_4f816d475bb0b9ed640ae412d6b42cab=1719824729; "
                  "__utmc=63332592; _qzjc=1; _jzqc=1; sdc_userflag=1721568321596::1721568321596::1; "
                  "CLICKSTRN_ID=117656264-1641645328.322497::9EC7C1B74FA330E6AE13CA38948C2672",
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
            print("No match found")
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
        else:
            print("No match found")
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
        print(
            f"比赛ID: {fid_value} 场次: {cnum} 赛事: {Events} 轮次: {Rounds} 比赛时间: {matches_time} 状态: {state} 主队: {home_name} 客队: {away_name} 比分: {score} 让球: {rq}")
        print()
        await main(fid_value, Events, Rounds, home_name, matches_time)


async def main(fid_value, Events, Rounds, home_name, vs_date):
    """
    Main function to create and run tasks for fetching data from URLs in filtered_url_dict.
    """
    new_eu_url_dict = await get_europe_url(fid_value)
    new_asia_url_dict = await get_asia_url(fid_value, vs_date)

    eu_tasks = []
    asia_tasks = []

    semaphore = asyncio.Semaphore(5)  # 最多允许5个并发任务
    # 在创建任务时，传递额外的标识信息
    for url_name, url in new_eu_url_dict.items():
        eu_tasks.append(second_req(semaphore, url, url_name))

    for url_name, url in new_asia_url_dict.items():
        asia_tasks.append(second_req(semaphore, url, url_name))

    # 处理结果时，可以通过标识信息区分每个任务的返回值
    eu_results = await asyncio.gather(*eu_tasks)
    await asyncio.sleep(6.88)
    asia_results = await asyncio.gather(*asia_tasks)

    eu_results_csv = pd.DataFrame(eu_results)
    asia_results_csv = pd.DataFrame(asia_results)

    data_directory = f'./data/{Events}/{Rounds}'
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    eu_results_csv.to_csv("{}/{}_eu_results.csv".format(data_directory, home_name), index=False)
    asia_results_csv.to_csv("{}/{}_asia_results.csv".format(data_directory, home_name), index=False)

    for result in eu_results:
        print(f"URL Name: {result['name']}, Data: {result['data']}")

    print()
    print("\n")
    for result in asia_results:
        print(f"URL Name: {result['name']}, Data: {result['data']}")


# Run the main function
if __name__ == "__main__":
    t = time.time()
    # print(int(time.time() * 1000))
    # asyncio.run(get_eu_asia())
    asyncio.run(get_asia_url(1145346, "07-23 00:00"))
    print(f"Time taken: {time.time() - t} seconds.")
