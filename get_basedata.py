# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :get_basedata.py
# @Time      :2024/7/1 下午4:42
# @Author    :MA-X-J
# @Software  :PyCharm
# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :fb_data_gather.py
# @Time      :2024/4/10 上午11:11
# @Author    :MA-X-J
# @Software  :PyCharm
import chardet
import httpx
from parsel import Selector, selector


def get_basedata():
    """获取基础数据"""
    url = "https://odds.500.com/fenxi/shuju-1133203.shtml"
    headers = {
        "Host": "odds.500.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,"
                  "image/svg+xml,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Cookie": "WT_FPC=id=undefined:lv=17ww.baidu.com58b0000000664f046e4; isautologin0App=op_chupan; "
                  "ck=MjAyMzA4MTgwMDAwNTUzOTA1ZmM3MTcwODAzMTBjYWI2MDZiMWIwMTIyNjdiYmZh; sdc_session=16925g=140ae412d6",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Priority": "u=0, i",
        "TE": "trailers"
    }

    resp = httpx.get(url, headers=headers, timeout=10, verify=False)
    if resp.status_code == 200:
        resp = resp.content
        encoding = chardet.detect(resp)['encoding']
        html_content = resp.decode(encoding, 'ignore')
        selector_xpath = Selector(text=html_content)
        print(selector_xpath)


get_basedata()