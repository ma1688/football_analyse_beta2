# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :pl5.py
# @Time      :2024/1/16 18:32
# @Author    :MA-X-J
# @Software  :PyCharm
import json

import httpx
import numpy as np
import pandas as pd


def fetch_lottery_data(game_no, province_id, page_size, is_verify, term_limits, page_no):
    data_list = []
    headers = {
        "authority": "webapi.sporttery.cn",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-CN,zh;q=0.9",
        "origin": "https://m.sporttery.cn",
        "referer": "https://m.sporttery.cn/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, "
                      "like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    }

    params = {
        "gameNo": game_no,
        "provinceId": province_id,
        "pageSize": page_size,
        "isVerify": is_verify,
        "termLimits": term_limits,
        "pageNo": page_no
    }

    response = httpx.get("https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry", headers=headers,
                         params=params, verify=False, timeout=16.88)

    resp = json.loads(response.text)
    if resp.get("success"):
        resp_list = resp.get("value").get("list")
        for resp_data in resp_list:
            lotteryDrawNum = resp_data.get("lotteryDrawNum")  # 期数
            lotteryDrawTime = resp_data.get("lotteryDrawTime")  # 日期
            lotteryUnsortDrawresult = resp_data.get("lotteryDrawResult")
            print(f"期数: {lotteryDrawNum}----日期: {lotteryDrawTime}---->>>>结果: {lotteryUnsortDrawresult}")
            dict1 = {"期数": lotteryDrawNum,
                     "日期": lotteryDrawTime,
                     "开奖结果": lotteryUnsortDrawresult}
            data_list.append(dict1)
        df = pd.DataFrame(data_list)
        df.to_csv("./pl5.csv", index=False, header=True, encoding='utf-8-sig')


def analyse_data():
    """
    排列五分析
    :return:
    """

    # 读取数据
    df = pd.read_csv("./pl5.csv")
    kj_data = df["开奖结果"].head(50).tolist()
    kj_data = [x.split(" ") for x in kj_data]
    # 构造矩阵
    matrix = np.array(kj_data, dtype=int)

    print(matrix.shape)

    # 分解 为5 * 5的矩阵
    matrix = matrix[:, 0:5]
    print(matrix.shape)
    print(matrix)


if __name__ == "__main__":
    # for i in range(1):
    #     a = 1
    #     fetch_lottery_data("350133", "0", "100", "1", "0", a + i)
    #
    #     print("已保存期数: ", a + i)

    fetch_lottery_data("350133", "0", "100", "1", "0", 1)
    # analyse_data()