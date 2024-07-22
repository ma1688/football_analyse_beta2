# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :base_data.py
# @Time      :2024/7/21 下午7:04
# @Author    :MA-X-J
# @Software  :PyCharm
import logging
import os
import random
import time

import chardet
import httpx
import pandas as pd
from bs4 import BeautifulSoup
from parsel import Selector

# 创建一个logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # 设置logger的级别为INFO

# 创建一个handler，用于写入日志文件
log_directory = f'./data/log/'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
fh = logging.FileHandler(f'{log_directory}base_data.log')
fh.setLevel(logging.ERROR)  # 设置handler级别为ERROR

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)  # 为文件handler设置格式

# 给logger添加handler
logger.addHandler(fh)

# 设置基础配置的日志级别为ERROR
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_random_user_agent():
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


# 请求数据
def get_base_data(f_id):
    """
    获取基本数据
    :param f_id: 比赛ID
    :return: Selector
    """
    base_url = "https://odds.500.com/fenxi/shuju-{}.shtml".format(f_id)

    headers = {
        "Host": "odds.500.com",
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,"
                  "image/svg+xml,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
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
        "TE": "trailers"
    }
    try:
        resp = httpx.get(url=base_url, headers=headers, timeout=10, verify=False)
        content = resp.content
        # 检测编码格式
        result = chardet.detect(content)

        encoding = result['encoding']
        # 解码HTML代码片段
        html_content = content.decode(encoding, "ignore")

        selector = Selector(text=html_content)
        return selector

    except Exception as e:
        logger.error(e)
        return None


# 解析保存数据
def parse_html(selector, event, Rounds, home_name, away_name):
    """
    解析数据

    :param selector: Selector
    :param event: 赛事
    :param Rounds: 轮次
    :param home_name: 主队名称
    :param away_name: 客队名称
    :return: dict
    """

    "赛前联赛积分排名表格"
    home_rank_data = selector.xpath('//div[8]/div[2]/div[3]/div[1]/table/tbody/tr/td/text()').getall()
    away_rank_data = selector.xpath('//div[8]/div[2]/div[3]/div[2]/table/tbody/tr/td/text()').getall()
    "交战历史"
    if not selector.xpath('//div[3]/div[3]/table/tr').getall():
        history_data = selector.xpath('//div[4]/div[3]/table/tr').getall()
    else:
        history_data = selector.xpath('//div[3]/div[3]/table/tr').getall()

    "主(1)客(2)队近期战绩表格"
    for i in range(1, 3):
        home_recent_data = selector.xpath(
            f'//div[{i}]/form/div[3]/table/tbody/tr').getall()
        if i == 1:
            data_name = "home"
            data_name1 = home_name
        else:
            data_name = "away"
            data_name1 = away_name
        save_recent_data(home_recent_data, data_name, event, Rounds, data_name1)
    save_recent_data(history_data, "history", event, Rounds, home_name)
    print("\033[92m近期数据已经保存\033[0m")
    return home_rank_data, away_rank_data


def save_recent_data(recent_data, name_type, Events, Rounds, team_name):
    """
    保存近期比赛数据
    :param recent_data:
    :param name_type: history, home, away
    :param Events:  赛事
    :param Rounds: 轮次
    :param team_name: 球队名称
    :return:
    """
    data_directory = f'./data/{Events}/{Rounds}'
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    if recent_data:
        # 假定 home_recent_data 是你提供的数据列表
        matches = []
        for item in recent_data:
            # 为每一项数据创建一个 BeautifulSoup 对象
            soup = BeautifulSoup(item, 'lxml')
            row = soup.find('tr')  # 直接找到每项数据中的 tr 元素
            if row:
                cells = row.find_all('td')
                if cells:
                    league = cells[0].text.strip()
                    date = cells[1].text.strip()
                    match_title = cells[2].find('a', title=True).get('title', '').split('数据分析')[0] if cells[
                        2].find(
                        'a') else '未知比赛'
                    score = cells[2].find('em').text.strip() if cells[2].find('em') else '未知比分'

                    if len(cells) > 3:
                        handicap = cells[3]['title'] if 'title' in cells[3].attrs else '未知盘口'
                    else:
                        handicap = '未知盘口'
                    half_time_score = cells[4].text.strip()
                    result = cells[5].text.strip() if name_type in ["home", "away"] else cells[4].text.strip()
                    path = cells[6].text.strip()
                    size = cells[7].text.strip()

                    ouzhi_finall = cells[5].text.strip()
                    pankou = cells[6].text.strip()
                    pan_result = cells[7].text.strip()
                    sb = cells[7].text.strip() if name_type in ["home", "away"] else cells[8].text.strip()

                    matchs_list_type = {
                        '赛事': league,
                        '比赛日期': f'{date}',
                        '比赛': match_title,
                        '比分': score,
                        '盘口': handicap,
                        '半场比分': half_time_score,
                        '赛果': result,
                        '盘路': path,
                        '大小': size
                    } if name_type in ["home", "away"] else {
                        '赛事': league,
                        '比赛日期': f'{date}',
                        '比赛': match_title,
                        '比分': score,
                        '赛果': result,
                        "欧指终赔": ouzhi_finall,
                        '盘口': pankou,
                        '盘路': pan_result,
                        '大小': sb
                    }
                    # 保存信息
                    matches.append(matchs_list_type)
        # print(matches)
        try:
            matches_pd = pd.DataFrame(matches)
            matches_pd.to_csv(f'./data/{Events}/{Rounds}/{team_name}_{name_type}.csv', index=False,
                              encoding='utf-8-sig')
        except Exception as e:
            logger.error(f"Error occurred while saving data: {e}")
            return False
    else:
        print("历史交锋数据为空")
        return False


def main_base_data(choose_list: list):
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
        sr_data = get_base_data(fid_value)
        parse_html(sr_data, Events, Rounds, home_name, away_name)
        time.sleep(1.68)

#
# if __name__ == '__main__':
#     fid = 1145739
#     selector_data = get_base_data(fid)
#     parse_html(selector_data)
