# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :matches.py
# @Time      :2024/8/14 18:34
# @Author    :MA-X-J
# @Software  :PyCharm
import asyncio
import random
import re

import chardet
import httpx
from parsel import Selector
from prettytable import PrettyTable

from logger import logger


class MatchLive:
    """
    赛事直播页
    """

    def __init__(self, expect=24083):
        self.expect = expect

    @staticmethod
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

    async def get_headers(self):
        """
        获取请求头headers
        :return:
        """
        return {
            "Host": "live.500.com",
            "User-Agent": await self.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,"
                      "image/svg+xml,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://live.500.com/",
            "Connection": "keep-alive",
            "Cookie": "ck_RegFromUrl=https%3A//www.baidu.com/link%3Furl",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=4",
            "TE": "trailers"
        }

    @staticmethod
    async def get_proxy(ip_num: int):
        """
        获取代理
        :return: list
        """
        url = "https://api.douyadaili.com/proxy/?"
        data = {
            "service": "GetIp",
            "authkey": "7SGItHKgKhLAkRPMh8xX",
            "num": ip_num,
            "lifetime": 1,
            "prot": 0,
            "format": "json",
            "distinct": 10
        }
        username = "lm1688"
        password = "lm1688"
        resp_data = httpx.get(url=url, params=data).json()['data']
        proxy_list = []
        for resp in resp_data:
            ip = resp['ip']
            port = resp['port']
            proxy_list.append({
                "http://": f"http://{username}:{password}@{ip}:{port}",
                "https://": f"http://{username}:{password}@{ip}:{port}",
            })
        return proxy_list

    async def get_match_index(self):
        """
        获取赛事直播首页
        :return:
        """
        url = 'https://live.500.com/zqdc.php?e={}'.format(self.expect)

        proxy_ip = await self.get_proxy(1)
        try:
            resp = httpx.get(url, headers=await self.get_headers(), timeout=10, verify=False, proxies=proxy_ip[0])
            if resp.status_code == 200:
                return resp.content
            else:
                return None
        except Exception as e:
            logger.error(e)
            return None

    @staticmethod
    async def parse_html_content(html_data):
        """
        解析HTML内容
        :return:
        """
        if html_data:
            try:
                resp = html_data
                encoding = chardet.detect(resp)['encoding']
                html_content = resp.decode(encoding, 'ignore')
                selector_xpath = Selector(text=html_content)
                return selector_xpath
            except Exception as e:
                logger.error(f"Error occurred while parsing HTML content: {e}")
                return None
        else:
            logger.error("HTML content is empty.")
            return None

    async def select_data(self, selector):
        try:
            match_data_xpath = selector.xpath("//tbody/tr").getall()
            parse_data = []
            for match in match_data_xpath:
                data = await self.parse_html(match)
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
            logger.info(table)
            return parse_data

        except Exception as e:
            logger.error(f"Error occurred while parsing HTML content: {e}")
            return None

    @staticmethod
    async def parse_html(text):
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
        return extracted_data


if __name__ == '__main__':
    logger.info("Start to get match live data.")
    expect_num = int(input("请输入期数: "))
    logger.warning(f"期数: {expect_num}")
    # 初始化实列
    match = MatchLive()
    # 获取赛事直播首页
    html_data = asyncio.run(match.get_match_index())
    # 解析HTML
    selector = asyncio.run(match.parse_html_content(html_data))
    # 选择数据
    asyncio.run(match.select_data(selector))
