# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :get_euodds.py
# @Time      :2024/7/1 下午4:52
# @Author    :MA-X-J
# @Software  :PyCharm
from datetime import datetime

import chardet
import httpx
from parsel import Selector


def get_odds():
    """
    获取欧赔数据
    :return:
    """
    url = "https://odds.500.com/fenxi/yazhi-1133203.shtml"
    headers = {
        "Host": "odds.500.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://live.500.com/",
        "Connection": "keep-alive",
        "Cookie": "WT_FPC=id=undefined:lv==63332592.7.10.utmcmd=(none); __utmt=8; regfrom=0%7Cala%7Cbaidu; ck_RegUrl=odds.500.com; pcTouchDownload500App=op_chupan; ck=MjAyMzA4MTgwMDAwNTUzOTA1ZmM3MTcwODAz162; Hm_l.32249",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=0, i",
        "TE": "trailers"
    }

    resp = httpx.get(url=url, headers=headers, timeout=10, verify=False)
    if resp.status_code == 200:
        content = resp.content
        # 检测编码格式
        result = chardet.detect(content)

        encoding = result['encoding']
        # 解码HTML代码片段
        html_content = content.decode(encoding, 'ignore')

        selector = Selector(text=html_content)
        return selector
    else:
        return None


def convert_to_datetime(self, a):
    year = self.now.year
    date_time_str = str(year) + '-' + a + ':00'

    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    return date_time_obj


def get_asia_data(fid, vsdate):
    """
    获取亚赔初盘同赔
    :param fid:
    :param vsdate:
    :return:
    """
