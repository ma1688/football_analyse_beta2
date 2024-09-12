# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :get_sl_pass.py
# @Time      :2024/8/27 23:42
# @Author    :MA-X-J
# @Software  :PyCharm
import os

import chardet
import httpx
import pandas as pd
from parsel import Selector


class KJ:
    def __init__(self, expect):
        """
        初始化
        """
        self.expect = expect
        self.url = "https://zx.500.com/zqdc/kaijiang.php"
        self.headers = {
            "authority": "zx.500.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                      "*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": "showtips=1; sdc_session=1685103516984;",
            "referer": "https://zx.500.com/zqdc/kaijiang.php?playid=1&expect={}".format(self.expect),
            "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/119.0.0.0 Safari/537.36"
        }

    def get_sf(self):
        """获取开奖数据"""
        params = {
            "playid": "6",
            "expect": self.expect,
        }

        r = httpx.get(self.url, headers=self.headers, params=params, verify=False, timeout=8.8)

        content = r.content
        # 检测编码格式
        result = chardet.detect(content)

        encoding = result['encoding']
        # 解码HTML代码片段
        html_content = content.decode(encoding, 'ignore')

        selector_data = Selector(text=html_content)

        match_list = []
        round_num = len(selector_data.xpath("//div[3]/div/table[1]/tr/td[1]/text()").getall())

        xpath_s = {
            "场次": "//div[3]/div/table[1]/tr[{}]/td[1]/text()",
            "赛事": "//div[3]/div/table[1]/tr[{}]/td[2]/a/text()",
            "联赛": "//div[3]/div/table[1]/tr[{}]/td[3]/a/text()",
            "比赛时间": "//div[3]/div/table[1]/tr[{}]/td[4]/text()",
            "主队": "//div[3]/div/table[1]/tr[{}]/td[5]/a/text()",
            "盘口": "//div[3]/div/table[1]/tr[{}]/td[6]/span/text()",
            "客队": "//div[3]/div/table[1]/tr[{}]/td[7]/a/text()",
            "比分": "//div[3]/div/table[1]/tr[{}]/td[8]/text()",
            "胜平负": "//div[3]/div/table[1]/tr[{}]/td[9]/text()",
            "胜平负SP": "//div[3]/div/table[1]/tr[{}]/td[11]/text()"
        }

        for ii in range(2, round_num + 2):
            match_dict = {key: selector_data.xpath(xpath.format(ii)).get() for key, xpath in xpath_s.items()}
            match_list.append(match_dict)

        match_list = [match for match in match_list if match["赛事"] == "足球"]
        "重写场次序号"
        # Use a list comprehension to optimize the code
        match_list = [{**match, "场次": i + 1} for i, match in enumerate(match_list)]

        sf = pd.DataFrame(match_list)
        return sf

    def get_kj(self):
        """获取开奖数据"""

        params = {
            "playid": "0",
            "expect": self.expect,
        }

        r = httpx.get(self.url, headers=self.headers, params=params, verify=False, timeout=8.8)
        content = r.content

        # 检测编码格式
        result = chardet.detect(content)
        encoding = result['encoding']

        # 解码HTML代码片段
        html_content = content.decode(encoding, 'ignore')
        selector_data = Selector(text=html_content)

        # 提取数据
        data_fields = {
            "场次": "//div[3]/div/table[1]/tr[position() >= 2]/td[1]/text()",
            "赛事类型": "//div[3]/div/table[1]/tr[position() >= 2]/td[2]/a/text()",
            "比赛时间": "//div[3]/div/table[1]/tr[position() >= 2]/td[3]/text()",
            "主队": "//div[3]/div/table[1]/tr[position() >= 2]/td[4]/a/text()",
            "让球": "//div[3]/div/table[1]/tr[position() >= 2]/td[5]/span/text()",
            "客队": "//div[3]/div/table[1]/tr[position() >= 2]/td[6]/a/text()",
            "比分": "//div[3]/div/table[1]/tr[position() >= 2]/td[7]/text()",
            "让球胜平负彩果": "//div[3]/div/table[1]/tr[position() >= 2]/td[9]/text()",
            "让球胜平负SP": "//div[3]/div/table[1]/tr[position() >= 2]/td[10]/span/text()",
            "总进球数彩果": "//div[3]/div/table[1]/tr[position() >= 2]/td[12]/text()",
            "总进球数SP": "//div[3]/div/table[1]/tr[position() >= 2]/td[13]/span/text()",
            "比分彩果": "//div[3]/div/table[1]/tr[position() >= 2]/td[15]/text()",
            "比分SP": "//div[3]/div/table[1]/tr[position() >= 2]/td[16]/span/text()",
            "上下单双彩果": "//div[3]/div/table[1]/tr[position() >= 2]/td[18]/text()",
            "上下单双彩果SP": "//div[3]/div/table[1]/tr[position() >= 2]/td[19]/span/text()",
            "半全场彩果": "//div[3]/div/table[1]/tr[position() >= 2]/td[21]/text()",
            "半全场彩果SP": "//div[3]/div/table[1]/tr[position() >= 2]/td[22]/span/text()",
        }

        extracted_data = {key: selector_data.xpath(xpath).getall() for key, xpath in data_fields.items()}

        # 清理比赛时间
        extracted_data["比赛时间"] = [tt.replace('(', "").replace(")", "") for tt in extracted_data["比赛时间"] if tt]

        # 对数据进行对齐处理
        for index, value in enumerate(extracted_data["比分"]):
            if value == '-':
                if index >= len(extracted_data["让球胜平负彩果"]) or extracted_data["让球胜平负彩果"][index] != '-':
                    for key in ["让球胜平负彩果", "让球胜平负SP", "总进球数彩果", "总进球数SP", "比分彩果", "比分SP",
                                "上下单双彩果", "上下单双彩果SP",
                                "半全场彩果", "半全场彩果SP"]:
                        extracted_data[key].insert(index, '-' if '彩果' in key else '1.00')

        # 去除字典中列表的空元素
        kj_data = {key: list(filter(lambda x: x and x.strip(), value)) for key, value in extracted_data.items()}

        kj_data = pd.DataFrame(kj_data)

        return kj_data

    def merge_data(self):
        """
        合并数据
        :return:
        """

        kj_data = self.get_kj()
        sf_data = self.get_sf()

        # 确保 '场次' 列的数据类型一致
        kj_data['场次'] = kj_data['场次'].astype(str)
        sf_data['场次'] = sf_data['场次'].astype(str)

        merged_df = pd.merge(kj_data, sf_data[['场次', '盘口', '胜平负', '胜平负SP']], on='场次', how='left')

        # Ensure the directory exists
        output_dir = './data/spf_pass'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        merged_df.to_csv(f'./data/spf_pass/{self.expect}.csv', index=False)

        return merged_df

    def query_rq(self, home_name):
        """查询胜平负过关让球"""
        try:
            pd_data = pd.read_csv(f'./data/spf_pass/{self.expect}.csv')
            home_data = pd_data[pd_data["主队"].isin([home_name])]
            rq = home_data["盘口"]
            return rq
        except FileNotFoundError:
            print(f"Error: File './data/spf_pass/{self.expect}.csv' not found.")
        except KeyError as e:
            print(f"Error: Key {e} not found in the DataFrame.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return 0


def Analyse_data():
    """
    分析数据
    :return:
    """
    for i in range(24081, 24086):
        data = pd.read_csv(f'./data/spf_pass/{i}.csv')
        half_result = data["盘口"].value_counts()
        half_result_sp = data["胜平负"].value_counts()
        print(f"期数: {i}  {half_result}, {half_result_sp}")


if __name__ == "__main__":
    kj = KJ(24093)
    kj.merge_data()
    # Analyse_data()
