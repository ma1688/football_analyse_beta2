# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :get_sl_pass.py
# @Time      :2024/8/27 23:42
# @Author    :MA-X-J
# @Software  :PyCharm
import chardet
import httpx
import pandas as pd
from parsel import Selector

new_match_dist = {}


def get_kj(expect):
    """获取开奖数据"""
    url = "https://zx.500.com/zqdc/kaijiang.php"
    headers = {
        "authority": "zx.500.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": "showtips=1; sdc_session=1685103516984; _jzqc=1; __utmc=63332592; pcTouchDownload500App=btn_follow; ck_RegFromUrl=https^%^3A//www.baidu.com/link^%^3Furl^%^3Dcql8BONQbLTCEHROnXpAWFHWm2hd02RVEiKLRK4t3jPamKV-Annxw7ZE_6BQ3iaXv5K2INKbI5cDpyZxDsSLMq^%^26wd^%^3D^%^26eqid^%^3Dc5df59820002005a0000000664e83c73; ck_RegUrl=odds.500.com; _jzqy=1.1692941431.1692947433.1.jzqsr=baidu.-; __utmz=63332592.1692947434.37.5.utmcsr=baidu^|utmccn=(organic)^|utmcmd=organic; repeat69989f90223482523261fb81b7d63f18=1da821defa951749e176bd249983f39c; Hm_lvt_4f816d475bb0b9ed640ae412d6b42cab=1699420297; _qzjc=1; _jzqx=1.1685253742.1700304792.22.jzqsr=odds^%^2E500^%^2Ecom^|jzqct=/.jzqsr=odds^%^2E500^%^2Ecom^|jzqct=/; _jzqa=1.1798605657026601700.1685103517.1700304792.1700395806.62; _jzqckmp=1; __utma=63332592.1232481184.1685103519.1700304793.1700395807.61; __utmt=1; tgw_l7_route=628762f1b9e8827437e55a8d19ba77dd; WT_FPC=id=undefined:lv=1700396048233:ss=1700395812216:sdc_userflag=1700395805322::1700396048235::6; _qzja=1.1685190176.1700227943242.1700227943242.1700395812266.1700395977423.1700396048248.0.0.0.5.2; _qzjb=1.1700395812266.4.0.0.0; _qzjto=4.1.0; _jzqb=1.6.10.1700395806.1; Hm_lpvt_4f816d475bb0b9ed640ae412d6b42cab=1700396048; CLICKSTRN_ID=117.183.226.154-1685103517.484172::534A57305B610F8781752306BB9D9961; __utmb=63332592.6.10.1700395807; motion_id=1700396050026_0.24452878018973734",
        "referer": "https://zx.500.com/zqdc/kaijiang.php?playid=1&expect=23113",
        "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    params = {
        "playid": "6",
        "expect": expect,
    }

    r = httpx.get(url, headers=headers, params=params, verify=False, timeout=8.8)

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
        print(*match_dict.values())
        match_list.append(match_dict)

    match_list = [match for match in match_list if match["赛事"] == "足球"]
    pd.DataFrame(match_list).to_csv(f'./data/spf_pass/{expect}.csv', index=False, encoding='utf-8-sig')


get_kj(24091)
