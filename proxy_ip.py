# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :proxy_ip.py
# @Time      :2024/7/23 下午1:24
# @Author    :MA-X-J
# @Software  :PyCharm

import httpx


def get_proxy_ip():
    """
    获取代理IP
    :return:
    """
    base_url = "http://1.14.239.79:6008/get/"
    url_params = {
        "type": "https"
    }
    resp = httpx.get(url="http://1.14.239.79:6008/count/").json()
    print(resp)


if __name__ == '__main__':
    get_proxy_ip()
