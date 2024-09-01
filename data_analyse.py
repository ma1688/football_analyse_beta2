# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :data_analyse.py
# @Time      :2024/7/26 下午9:37
# @Author    :MA-X-J
# @Software  :PyCharm
import asyncio
import time

import pandas as pd
from colorama import Fore, Style

from logger import logger
from new_asia import get_instant_asia_odds, get_instant_europe_odds

pd.set_option('display.max_columns', 128)


class BaseAnalyseMethod:
    def __init__(self, rq: int):
        self.pan_dict = {
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
        self.rq = int(rq)

    def stoa(self, target_value):
        """
        亚盘转换
        :param target_value: 目标值
        :return: 转换后的盘口
        """
        try:
            new_pan = self.pan_dict[target_value]
            return new_pan
        except Exception as e:
            logger.error(f"{Fore.RED}转换出错: {e}{Style.RESET_ALL}")
            return False

    # 大小球
    @staticmethod
    async def analyse_big_small(r_data):
        """
        大小球分析
        :param r_data:
        :return:
        """
        try:
            big, small = 0, 0
            for score_data in r_data['比分']:
                # 去除比分中未开赛的  "VS
                if "VS" in score_data:
                    continue
                score_home, score_away = map(int, score_data.split(":"))

                if score_home + score_away > 2.5:
                    big += 1
                else:
                    small += 1

            total = big + small
            return {"big_goals": big / total, "small_goals": small / total}

        except Exception as e:
            logger.error(f"{Fore.RED}分析大小球出错: {e}{Style.RESET_ALL}")
            return False

    # 总进球数
    @staticmethod
    async def analyse_total_goal(r_data):
        """
        总进球数分析
        :param r_data:
        :return:
        """
        try:
            # 进球数
            goal_dict = {}
            for score_data in r_data['比分']:
                if "VS" in score_data:
                    continue
                score_home, score_away = map(int, score_data.split(":"))
                total_goal = score_home + score_away
                if total_goal not in goal_dict:
                    goal_dict[total_goal] = 1
                else:
                    goal_dict[total_goal] += 1

            return goal_dict

        except Exception as e:
            logger.error(f"{Fore.RED}分析总进球数出错: {e}{Style.RESET_ALL}")
            return False

    # 比分
    @staticmethod
    async def analyse_score(r_data):
        """
        比分分析
        :param r_data:
        :return:
        """

        try:
            # 比分
            score_dict = {}
            for score_data in r_data['比分']:
                if "VS" in score_data:
                    continue
                if score_data not in score_dict:
                    score_dict[score_data] = 1
                else:
                    score_dict[score_data] += 1

            return score_dict
        except Exception as e:
            logger.error(f"{Fore.RED}分析比分出错: {e}{Style.RESET_ALL}")
            return False

    # 胜平负
    @staticmethod
    async def analyse_win_draw_lose(r_data):
        """
        胜平负分析
        :param r_data:
        :return:
        """
        try:
            wdl_dict = {"win": 0, "draw": 0, "lose": 0}
            wdl = r_data[r_data['赛果'] != '-']['赛果'].value_counts(normalize=True)
            for key, value in wdl.items():
                if key == "胜":
                    wdl_dict["win"] = value
                elif key == "平":
                    wdl_dict["draw"] = value
                elif key == "负":
                    wdl_dict["lose"] = value

            return wdl_dict
        except Exception as e:
            logger.error(f"{Fore.RED}分析胜平负出错: {e}{Style.RESET_ALL}")
            return False

    # 让球胜平负
    async def analyse_let_ball_win_draw_lose(self, r_data):
        """
        让球胜平负分析
        :param r_data:
        :return:
        """
        try:
            rq_spf = {"rq_win": 0, "rq_draw": 0, "rq_lose": 0}
            total_matches = 0
            for score_data in r_data['比分']:
                if "VS" in score_data:
                    continue
                score_home, score_away = map(int, score_data.split(":"))
                total_matches += 1
                if score_home + int(self.rq) > score_away:
                    rq_spf["rq_win"] += 1
                elif score_home + int(self.rq) == score_away:
                    rq_spf["rq_draw"] += 1
                else:
                    rq_spf["rq_lose"] += 1

            if total_matches > 0:
                rq_spf = {key: value / total_matches for key, value in rq_spf.items()}

            return rq_spf
        except Exception as e:
            logger.error(f"{Fore.RED}分析让球胜平负出错: {e}{Style.RESET_ALL}")
            return False

    # 盘路统计
    @staticmethod
    async def analyse_plate_road(r_data):
        """
        盘路统计
        :param r_data:
        :return:
        """
        try:
            pr_dict = {"win": 0, "zou": 0, "lose": 0}
            pr_data = r_data[r_data['盘路'] != '-']['盘路'].value_counts(normalize=True)

            for key, value in pr_data.items():
                if key == "赢":
                    pr_dict["win"] = value
                elif key == "走":
                    pr_dict["zou"] = value
                elif key == "输":
                    pr_dict["lose"] = value
            return pr_dict
        except Exception as e:
            logger.error(f"{Fore.RED}分析盘路出错: {e}{Style.RESET_ALL}")
            return False

    # 进失球数
    @staticmethod
    async def xa_goals(r_data):
        """
        进失球数
        :param r_data:
        :return:
        """
        xa_goals_dict = {"xxg": 0, "aag": 0}  # xxg: 进球数, aag: 失球数

        try:
            for score_data in r_data['比分']:
                if "VS" in score_data:
                    continue
                score_home, score_away = map(int, score_data.split(":"))
                xa_goals_dict["xxg"] += score_home
                xa_goals_dict["aag"] += score_away

            return xa_goals_dict

        except Exception as e:
            logger.error(f"{Fore.RED}分析进失球数出错: {e}{Style.RESET_ALL}")
            return False

    async def odds_analyse(self, data):

        if data.empty:
            return None
        spf_dict = {"win": 0, "draw": 0, "lose": 0}
        rq_qpf_dict = {"win": 0, "draw": 0, "lose": 0}

        # Now you can safely perform the addition operation
        scores = data['比分'].str.split(':', expand=True).astype(int)

        # *****************************************胜平负分析****************************************
        spf_dict["win"] = (scores[0] > scores[1]).sum()
        spf_dict["draw"] = (scores[0] == scores[1]).sum()
        spf_dict["lose"] = (scores[0] < scores[1]).sum()
        # ****************************************胜平负分析****************************************

        # ****************************************让球胜平负分析****************************************
        rq_qpf_dict["win"] = (scores[0] + self.rq > scores[1]).sum()
        rq_qpf_dict["draw"] = (scores[0] + self.rq == scores[1]).sum()
        rq_qpf_dict["lose"] = (scores[0] + self.rq < scores[1]).sum()
        # ****************************************让球胜平负分析****************************************

        # ****************************************大小球分析****************************************
        sb_dict = {"big": (scores[0] + scores[1] >= 3).sum(), "small": (scores[0] + scores[1] <= 2).sum()}
        # ****************************************大小球分析****************************************

        # ****************************************进球数分析****************************************
        total_goals_dict = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7+": 0}
        total_goals = scores[0] + scores[1]
        total_goals_dict["0"] = (total_goals == 0).sum()
        total_goals_dict["1"] = (total_goals == 1).sum()
        total_goals_dict["2"] = (total_goals == 2).sum()
        total_goals_dict["3"] = (total_goals == 3).sum()
        total_goals_dict["4"] = (total_goals == 4).sum()
        total_goals_dict["5"] = (total_goals == 5).sum()
        total_goals_dict["6"] = (total_goals == 6).sum()
        total_goals_dict["7+"] = (total_goals >= 7).sum()

        # ****************************************进球数分析****************************************

        # ****************************************比分分析****************************************
        score_dict = {}
        for i in range(len(scores)):
            score = str(scores.iloc[i, 0]) + "-" + str(scores.iloc[i, 1])
            if score in score_dict:
                score_dict[score] += 1
            else:
                score_dict[score] = 1
        # ****************************************比分分析****************************************
        # Calculate total number of matches
        total_matches = len(scores)

        # ****************************************盘路分析****************************************
        pr_dict = None
        if '盘路' in data.columns:
            pr_dict = {"win": ((data['盘路'] == '赢盘').sum()),
                       'zou': (data['盘路'] == '走盘').sum(),
                       'lose': (data['盘路'] == '输盘').sum()}
            pr_dict = {k: (v / total_matches) for k, v in pr_dict.items()}
        # ****************************************盘路分析****************************************

        # Convert counts to percentages
        spf_dict = {k: (v / total_matches)for k, v in spf_dict.items()}
        rq_qpf_dict = {k: (v / total_matches) for k, v in rq_qpf_dict.items()}
        sb_dict = {k: (v / total_matches) for k, v in sb_dict.items()}
        total_goals_dict = {k: (v / total_matches)for k, v in total_goals_dict.items()}
        score_dict = {k: (v / total_matches) for k, v in score_dict.items()}

        return spf_dict, rq_qpf_dict, sb_dict, total_goals_dict, score_dict, pr_dict


class TotalAnalyse:
    """总分析方法"""

    def __init__(self):
        self.weights = {
            'sb_goals': {
                '主队近期大小球': 0.2,
                '主队主场大小球': 0.15,
                '客队近期大小球': 0.2,
                '客队客场大小球': 0.15,
                '历史大小球': 0.1,
                'eu_odds': 0.1,
                'asia_odds': 0.1
            }
        }


# 分析最近数据
async def recent_data_analyse(Events, Rounds, home_name, away_name, rq=0):
    """
    分析最近数据
    :param Events: 赛事
    :param Rounds:  轮次
    :param home_name: 主队
    :param away_name: 客队
    :param rq: 让球
    :return:
    """
    fenxi = BaseAnalyseMethod(rq)

    file_path_home = r"D:\python\football_analyse_beta2\data\{}\{}\{}_home.csv".format(Events, Rounds, home_name)
    file_path_away = r"D:\python\football_analyse_beta2\data\{}\{}\{}_away.csv".format(Events, Rounds, away_name)
    file_path = [file_path_home, file_path_away]

    analyse_result = {}  # 分析结果

    try:
        for path_name in file_path:
            data = pd.read_csv(path_name)
            col_name = int(len(data['比赛日期']) / 2)
            recent_data = data[:col_name]  # 近期数据

            if "home" in path_name:
                """
                近期数据处理
                大小球, 总进球数, 胜平负, 盘路
                """

                analyse_result["主队近期大小球"] = await fenxi.analyse_big_small(recent_data)
                analyse_result["主队近期总进球数"] = await fenxi.analyse_total_goal(recent_data)
                analyse_result['主队近期胜平负'] = await fenxi.analyse_win_draw_lose(recent_data)
                analyse_result['主队近期盘路'] = await fenxi.analyse_plate_road(recent_data)

                """
                主客场数据分析
                大小球, 总进球数,比分 胜平负,让球胜平负, 盘路
                """
                ha_data = data[col_name:]
                analyse_result["主队主场大小球"] = await fenxi.analyse_big_small(ha_data)
                analyse_result["主队主场总进球数"] = await fenxi.analyse_total_goal(ha_data)
                analyse_result["主队主场比分"] = await fenxi.analyse_score(ha_data)
                analyse_result['主队主场胜平负'] = await fenxi.analyse_win_draw_lose(ha_data)
                analyse_result['主队主场让球胜平负'] = await fenxi.analyse_let_ball_win_draw_lose(ha_data)
                analyse_result['主队主场盘路'] = await fenxi.analyse_plate_road(ha_data)
                analyse_result['主队主场进失球数'] = await fenxi.xa_goals(ha_data)

            elif "away" in path_name:
                """
                     近期数据处理
                     大小球, 总进球数, 胜平负, 盘路
                     """

                analyse_result["客队近期大小球"] = await fenxi.analyse_big_small(recent_data)
                analyse_result["客队近期总进球数"] = await fenxi.analyse_total_goal(recent_data)
                analyse_result['客队近期胜平负'] = await fenxi.analyse_win_draw_lose(recent_data)
                analyse_result['客队近期盘路'] = await fenxi.analyse_plate_road(recent_data)

                """
                客客场数据分析
                大小球, 总进球数,比分 胜平负,让球胜平负, 盘路
                """
                ha_data = data[col_name:]
                analyse_result["客队客场大小球"] = await fenxi.analyse_big_small(ha_data)
                analyse_result["客队客场总进球数"] = await fenxi.analyse_total_goal(ha_data)
                analyse_result["客队客场比分"] = await fenxi.analyse_score(ha_data)
                analyse_result['客队客场胜平负'] = await fenxi.analyse_win_draw_lose(ha_data)
                analyse_result['客队客场让球胜平负'] = await fenxi.analyse_let_ball_win_draw_lose(ha_data)
                analyse_result['客队客场盘路'] = await fenxi.analyse_plate_road(ha_data)
                analyse_result['客队客场进失球数'] = await fenxi.xa_goals(ha_data)

    except FileExistsError as fi:
        logger.error("主客场数据文件不存在", fi)
    try:
        """
        分析历史数据 只分析主队
        大小球, 总进球数,比分 胜平负,让球胜平负, 盘路
        """
        file_history = r"D:\python\football_analyse_beta2\data\{}\{}\{}_history.csv".format(Events, Rounds,
                                                                                            home_name)
        data_history = pd.read_csv(file_history)
        analyse_result["历史大小球"] = await fenxi.analyse_big_small(data_history)
        analyse_result["历史总进球数"] = await fenxi.analyse_total_goal(data_history)
        analyse_result["历史比分"] = await fenxi.analyse_score(data_history)
        analyse_result['历史胜平负'] = await fenxi.analyse_win_draw_lose(data_history)
        analyse_result['历史盘路'] = await fenxi.analyse_plate_road(data_history)

    except FileExistsError as f:
        logger.error("历史数据文件不存在", f)

    finally:
        return analyse_result


# 分析欧盘数据
async def eu_odds_analyse(fid, Events, Rounds, home_name, deviation_value, rq=0):
    """
    欧盘数据分析
    :return:
    """

    new_odds = get_instant_europe_odds(fid)
    # new_odds = [2.75, 3.22, 2.43]
    data_path = r"D:\python\football_analyse_beta2\data\eu_odds\{}\{}\{}_eu_results.csv".format(Events, Rounds,
                                                                                                home_name)
    data = pd.read_csv(data_path)
    data['终赔'] = data['终赔'].apply(lambda x: [float(ii) for ii in eval(x)])
    data['赛事'] = data['赛事'].apply(lambda x: x.replace(" ", "").strip())

    logger.warning(f"赛事: {Events}   主队: {home_name}   即时赔率: {new_odds}  匹配误差: {deviation_value}")

    eu_fenxi = BaseAnalyseMethod(rq)

    # # 过滤出终赔符合条件的数据  误差在每个数据的-+0.08
    filter_events = Events
    enable_event_filter = False
    if filter_events:
        enable_event_filter = True  # 设置为 True 开启赛事筛选，设置为 False 则关闭赛事筛选
        if filter_events == "J1联赛" or filter_events == "J2联赛":
            filter_events = "日职"
        elif filter_events == "墨超":
            filter_events = "墨西联"

    new_data = data[
        ((data['赛事'] == filter_events) if enable_event_filter else True) &
        (data['终赔'].apply(
            lambda x: all([float(x[i]) - deviation_value <= float(new_odds[i]) <= float(x[i]) + deviation_value for i in
                           range(3)])))]

    if new_data.empty:
        logger.warning(f"暂时没有符合条件的数据")
        logger.warning(f"直接统计欧赔数据")
        all_new_data = data[(data['终赔'].apply(
            lambda x: all([float(x[i]) - deviation_value <= float(new_odds[i]) <= float(x[i]) + deviation_value
                           for i in range(3)])))]
        logger.info(f"{Fore.GREEN}符合条件的数据: {len(all_new_data)}{Style.RESET_ALL}\t\t"
                    f"{Fore.GREEN} odds误差: {deviation_value}{Style.RESET_ALL}")
        print(f"符合条件的数据: \n{all_new_data}\n")
        eu_analyse_data = await eu_fenxi.odds_analyse(all_new_data)
        return eu_analyse_data
    else:
        logger.info(f"{Fore.GREEN}符合条件的数据: {len(new_data)}{Style.RESET_ALL}\t\t"
                    f"{Fore.GREEN} odds误差: {deviation_value}{Style.RESET_ALL}")
        print(f"符合条件的数据: \n{new_data}\n")
        eu_analyse_data = await eu_fenxi.odds_analyse(new_data)
        return eu_analyse_data


# 分析亚盘数据
async def asia_odds_analyse(fid, Events, Rounds, home_name, deviation_value, rq=0):
    """
    亚盘数据分析
    :return:
    """
    # 获取即时赔率
    new_odds = get_instant_asia_odds(fid)
    asia_fenxi = BaseAnalyseMethod(rq)

    data_path = r"D:\python\football_analyse_beta2\data\asia_odds\{}\{}\{}_asia_results.csv".format(Events, Rounds,
                                                                                                    home_name)
    data = pd.read_csv(data_path)
    data['终赔'] = data['终赔'].apply(lambda x: [eval(x)[0], asia_fenxi.stoa(eval(x)[1]), eval(x)[2]])
    data['联赛'] = data['联赛'].apply(lambda x: x.replace(" ", "").strip())

    logger.warning(f"赛事: {Events}   主队: {home_name}   即时赔率: {new_odds}  匹配误差: {deviation_value}")

    # # 过滤出终赔符合条件的数据  误差在每个数据的-+0.08
    filter_events = Events
    enable_event_filter = False
    if filter_events:
        enable_event_filter = True  # 设置为 True 开启赛事筛选，设置为 False 则关闭赛事筛选
        if filter_events == "J1联赛" or filter_events == "J2联赛":
            filter_events = "日职"
        elif filter_events == "墨超":
            filter_events = "墨西联"
    new_data = data[
        (
            (data['联赛'] == filter_events) if enable_event_filter else True
        ) &
        (data['终赔'].apply(
            lambda x: all(
                [float(x[i]) - deviation_value <= float(new_odds[i]) <= float(x[i]) + deviation_value
                 for i in range(3)])))]

    if new_data.empty:
        logger.warning(f"暂时没有符合条件的数据")
        logger.warning(f"直接统计亚盘的数据")
        all_new_data = data[(data['终赔'].apply(
            lambda x: all([float(x[i]) - deviation_value <= float(new_odds[i]) <= float(x[i]) + deviation_value
                           for i in range(3)])))]
        logger.info(f"{Fore.GREEN}符合条件的数据: {len(all_new_data)}{Style.RESET_ALL}\t\t"
                    f"{Fore.GREEN} odds误差: {deviation_value}{Style.RESET_ALL}")
        print(f"符合条件的数据: \n{all_new_data}\n")
        asia_analyse_data = await asia_fenxi.odds_analyse(all_new_data)
        return asia_analyse_data
    else:
        logger.info(f"{Fore.GREEN}符合条件的数据: {len(new_data)}{Style.RESET_ALL}\t\t"
                    f"{Fore.GREEN} odds误差: {deviation_value}{Style.RESET_ALL}")
        print(f"符合条件的数据: \n{new_data}\n")
        asia_analyse_data = await asia_fenxi.odds_analyse(new_data)
        return asia_analyse_data


# 总分析
async def total_analyse(fid, Events, Rounds, home_name, away_name, deviation_value: list, rq=0):
    """
    总分析
    :return:
    """

    asia_value = deviation_value[0]
    eu_value = deviation_value[1]
    total_analyse_data = {"base_data": await recent_data_analyse(Events, Rounds, home_name, away_name, rq),
                          "eu_odds": await eu_odds_analyse(fid, Events, Rounds, home_name, eu_value, rq),
                          "asia_odds": await asia_odds_analyse(fid, Events, Rounds, home_name, asia_value, rq)}

    return total_analyse_data


if __name__ == '__main__':
    a = time.time()
    # asyncio.run(eu_odds_analyse(), debug=True)
    asyncio.run(eu_odds_analyse(1156661, "德甲", "第1轮", "沃尔夫斯堡", 0.618), debug=True)
    asyncio.run(asia_odds_analyse(1156661, "德甲", "第1轮", "沃尔夫斯堡", 0.168), debug=True)

    print(time.time() - a)
