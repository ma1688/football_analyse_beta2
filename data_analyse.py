# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :data_analyse.py
# @Time      :2024/7/26 下午9:37
# @Author    :MA-X-J
# @Software  :PyCharm
import time
import asyncio
import pandas as pd
from colorama import Fore, Style

from logger import logger


class AnalyseMethod:
    def __init__(self, rq: int, asia_min: int, asia_max: int, eu_max: int, eu_min: int):
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
        self.asia_min = asia_min  # 亚盘最小值
        self.asia_max = asia_max  # 亚盘最大值
        self.eu_min = eu_min  # 欧赔最小值
        self.eu_max = eu_max  # 欧赔最大值
        self.rq = rq

    # 亚盘口转换
    async def stoa(self, target_value):
        """
        亚盘转换
        :param target_value: 目标值
        :return: 转换后的盘口
        """
        try:
            for key, value in self.pan_dict.items():

                if float(target_value) > 0 and float(target_value) - value < self.asia_max:
                    return key

                elif float(target_value) < 0 and float(target_value) - value > self.asia_min:
                    return key

            raise ValueError("在字典中找不到值.")

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
                if score_home + self.rq > score_away:
                    rq_spf["rq_win"] += 1
                elif score_home + self.rq == score_away:
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
    fenxi = AnalyseMethod(rq, asia_min=3, asia_max=4, eu_max=4, eu_min=-4)

    file_path_home = r"D:\python\football_analyse_beta2\data\{}\{}\{}_home.csv".format(Events, Rounds, home_name)
    file_path_away = r"D:\python\football_analyse_beta2\data\{}\{}\{}_away.csv".format(Events, Rounds, away_name)
    file_history = r"D:\python\football_analyse_beta2\data\{}\{}\{}_history.csv".format(Events, Rounds, home_name)

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

        """
        分析历史数据 只分析主队
        大小球, 总进球数,比分 胜平负,让球胜平负, 盘路
        """

        data_history = pd.read_csv(file_history)
        analyse_result["历史大小球"] = await fenxi.analyse_big_small(data_history)
        analyse_result["历史总进球数"] = await fenxi.analyse_total_goal(data_history)
        analyse_result["历史比分"] = await fenxi.analyse_score(data_history)
        analyse_result['历史胜平负'] = await fenxi.analyse_win_draw_lose(data_history)
        analyse_result['历史盘路'] = await fenxi.analyse_plate_road(data_history)

        print(analyse_result)
        analyse_result = pd.DataFrame(analyse_result)
        analyse_result.to_excel(r"D:\python\football_analyse_beta2\data\{}\{}\{}_{}_analyse.xlsx".format(Events, Rounds, home_name, away_name), index=False)
        print(analyse_result)
        # analyse_result.to_csv(r"D:\python\football_analyse_beta2\data\{}\{}\{}_{}_analyse.csv".format(Events, Rounds, home_name, away_name), index=False)

        # return analyse_result
    except Exception as e:
        logger.error("--------------读取文件失败 or 文件不存在---------------------", e)


# 分析欧盘数据
def eu_odds_analyse():
    pass


# 分析亚盘数据
def asia_odds_analyse():
    pass


# 总分析
def total_analyse():
    pass


async def main():
    tasks = []
    for i in range(1):
        tasks.append(recent_data_analyse("奥运女足", "分组赛", "巴西女足", "西班牙女足", rq=0))
    await asyncio.gather(*tasks)



if __name__ == '__main__':
    a = time.time()
    asyncio.run(main())
    print(time.time() - a)

