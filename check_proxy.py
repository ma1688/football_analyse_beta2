# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :check_proxy.py
# @Time      :2024/7/23 下午1:25
# @Author    :MA-X-J
# @Software  :PyCharm
import httpx


def get_proxy_info(atype=4, anonymous=1, country="中国"):
    """
    通过API获取代理信息.

    参数:
    port (str): 端口号, 默认为 "8080,80"
    type (int): 代理协议类型 (1=http, 2=https, 3=socks4, 4=socks5), 默认为 1
    anonymous (int): 匿名类型 (1=透明, 2=普通, 3=高匿), 默认为 1
    country (str): 国家, 默认为 "中国"
    province (str): 省, 仅有中国地区数据才有此字段, 默认为 "江苏省"
    respType (str): 接口响应格式, 默认为 "json"

    返回:
    dict: 返回包含代理信息的字典
    """

    # Define the base URL
    url = "http://1.14.239.79:6168/api/get"

    # Define the parameters for the request
    params = {
        "type": atype,
        "anonymous": anonymous,
        "country": country,
    }

    # Send the GET request
    response = httpx.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        print(response.text)
        # return response.json()
    else:
        return {"error": "Request failed with status code {}".format(response.status_code)}


# Example usage
proxy_info = get_proxy_info()
print(proxy_info)
