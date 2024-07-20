# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :new_asia.py
# @Time      :2024/2/4 19:30
# @Author    :MA-X-J
# @Software  :PyCharm
import random

import chardet
import httpx
from parsel import Selector

HANDICAP_DICT = {
    "受平手/半球": 0.25,
    "受半球": 0.5,
    "受半球/一球": 0.75,
    "受一球": 1,
    "受一球/球半": 1.25,
    "受球半": 1.5,
    "受球半/两球": 1.75,
    "受两球": 2,
    "受两球/两球半": 2.25,
    "受两球半": 2.5,
    "受两球半/三球": 2.75,
    "受三球": 3,
    "受三球/三球半": 3.25,
    "受三球半": 3.5,
    "受三球半/四球": 3.75,
    "受四球": 4,
    "平手": 0,
    "平手/半球": -0.25,
    "半球": -0.5,
    "半球/一球": -0.75,
    "一球": -1,
    "一球/球半": -1.25,
    "球半": -1.5,
    "球半/两球": -1.75,
    "两球": -2,
    "两球/两球半": -2.25,
    "两球半": -2.5,
    "两球半/三球": -2.75,
    "三球": -3,
    "三球/三球半": -3.25,
    "三球半": -3.5,
    "三球半/四球": -3.75,
    "四球": -4,
}


def asian_handicap_convert(handicap):
    """亚盘转换"""
    return HANDICAP_DICT.get(handicap, None)


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
    return random.choice(USER_AGENT_LIST)


def get_headers(data_type='europe_jczq'):
    """获取请求头"""

    headers = {
        "Host": "odds.500.com",
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": f"https://odds.500.com/{data_type}.shtml",
        "Connection": "keep-alive",
        "Cookie": "WT_FPC=id=undefined:lv=1685165533972:ss=1685163136167; "
                  "ck_RegFromUrl=https%3A//www.baidu.com/link%3Furl%3D00sIkMo1CmoVbLFHbFFn0YNqRChnFRxAsc3yS_9xKru"
                  "%26wd%3D%26eqid%3Dd1daf6c0000973440000000664718d0d; "
                  "seo_key=baidu%7C%7Chttps://www.baidu.com/link?url=00sIkMo1CmoVbLFHbFFn0YNqRChnFRxAsc3yS_9xKru&wd"
                  "=&eqid=d1daf6c0000973440000000664718d0d; ck_regchanel=_ad0.7232252524252528; "
                  "regfrom=0%7Cala%7Cbaidu; sdc_session=1673351025935; motion_id=1685165533451_0.7706438216615666; "
                  "ck_RegUrl=odds.500.com; pcTouchDownload500App=op_chupan; "
                  "sdc_userflag=1685163125522::1685165533972::24; tgw_l7_route=1708f7089570919168107aecc592756d",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }
    return headers


# ##############################数据获取################################
def get_asia_odds(fid):
    """
    获取各家盘口url
    :param fid:
    :param url:
    :return:  selector
    """
    url = f"//odds.500.com/fenxi/yazhi-{fid}.shtml"
    try:
        response = httpx.get(url='https:' + url, headers=get_headers(), verify=False, timeout=8.8)

        content = response.content
        # 检测编码格式
        result = chardet.detect(content)

        encoding = result['encoding']
        # 解码HTML代码片段
        html_content = content.decode(encoding, 'ignore')

        selector = Selector(text=html_content)

        avg_now_xpath = "//tr[1]/td[3]/table/tbody/tr/td/text()"
        avg_last_xpath = "//tr[1]/td[5]/table/tbody/tr/td[2]/text()"
        max_now_xpath = "//tr[2]/td[2]/table/tbody/tr/td[2]/text()"
        max_last_xpath = '//tr[2]/td[4]/table/tbody/tr/td[2]/text()'
        min_now_xpath = "//tr[3]/td[3]/table/tbody/tr/td[2]/text()"
        min_last_xpath = "//tr[3]/td[5]/table/tbody/tr/td[2]/text()"

        "//tr[1]/td[3]/table/tbody/tr/td[2]"
        "//tr[2]/td[2]/table/tbody/tr/td[2]"
        "//tr[3]/td[3]/table/tbody/tr/td[2]"
        "/html/body/div[9]/div[3]/table/tbody/tr[1]/td[5]/table/tbody/tr/td[2]"
        "/html/body/div[9]/div[3]/table/tbody/tr[2]/td[4]/table/tbody/tr/td[2]"
        '/html/body/div[9]/div[3]/table/tbody/tr[3]/td[5]/table/tbody/tr/td[2]'

        # print(selector.xpath(avg_now_xpath).getall()[4:5])
        # print(selector.xpath(max_now_xpath).getall())
        # print(selector.xpath(min_now_xpath).getall()[1:])
        # print()
        # print(selector.xpath(avg_last_xpath).getall()[:1])
        # print(selector.xpath(max_last_xpath).getall())
        # print(selector.xpath(min_last_xpath).getall()[1:])

        "转换亚盘值"
        avg_now_value = selector.xpath(avg_now_xpath).getall()[4:5][0]
        max_now_value = asian_handicap_convert(selector.xpath(max_now_xpath).getall()[0])
        min_now_value = asian_handicap_convert(selector.xpath(min_now_xpath).getall()[1:][0])
        print(f"即时亚盘均值: {avg_now_value}  最大值: {max_now_value}   最小值: {min_now_value}")

        avg_last_value = asian_handicap_convert(selector.xpath(avg_last_xpath).getall()[:1][0])
        max_last_value = asian_handicap_convert(selector.xpath(max_last_xpath).getall()[0])
        min_last_value = asian_handicap_convert(selector.xpath(min_last_xpath).getall()[1:][0])
        print(f"初盘亚盘均值: {avg_last_value}  最大值: {max_last_value}   最小值: {min_last_value}")

    except Exception as e:
        print(f"get各家url时出错: {e}\r\n")


if __name__ == "__main__":
    fid = 1092967
    get_asia_odds(fid)
