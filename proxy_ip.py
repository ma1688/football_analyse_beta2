# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :proxy_ip.py
# @Time      :2024/7/23 下午1:24
# @Author    :MA-X-J
# @Software  :PyCharm

import concurrent.futures

import requests


def test_proxy(port):
    url = 'http://httpbin.org/ip'  # 一个返回请求IP的测试网址
    proxies = {
        "http": f"http://127.0.0.1:{port}",
        "https": f"https://127.0.0.1:{port}"
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            return f"Proxy {proxies} is working. Response: {response.json()}"
        else:
            return f"Proxy {proxies} is not working. Status Code: {response.status_code}"
    except requests.exceptions.ProxyError:
        return f"Proxy {proxies} is not working. Proxy Error."
    except requests.exceptions.ConnectTimeout:
        return f"Proxy {proxies} is not working. Connection Timeout."
    except requests.exceptions.RequestException as e:
        return f"Proxy {proxies} is not working. Error: {e}"


def main():
    ports = range(1688,1689)
    with concurrent.futures.ThreadPoolExecutor(max_workers=128) as executor:
        results = list(executor.map(test_proxy, ports))
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
