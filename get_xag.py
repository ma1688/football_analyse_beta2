# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :get_xag.py
# @Time      :2024/8/20 16:05
# @Author    :MA-X-J
# @Software  :PyCharm


import httpx
import pandas as pd

from logger import logger


def colorize_value(value):
    color = "\033[92m" if value > 0 else "\033[91m"
    return f"{color}{value}\033[0m"


def get_xg_data():
    """
    获取XG XAG数据
    :return:
    """

    url = "https://www.fotmob.com/api/tltable?leagueId=47"
    url_params = {
        "leagueId": 47  # 47 英超
    }
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    try:
        response = httpx.get(url, headers=headers)
        data = response.json()[0]['data']['table']['xg']
        xg_list = []

        # Calculate column widths
        max_widths = {
            "rank": len("排名"),
            "rank_diff": len("排名变化"),
            "team": len("球队"),
            "xG": len("xG"),
            "xG_Diff": len("xGDiff"),
            "xGA": len("xGA"),
            "xGA_Diff": len("xGADiff"),
            "x_pts": len("积分"),
            "x_points": len("xPoints"),
            "x_points_diff": len("xPointsDiff")
        }

        for team_data in data:
            team_name = team_data['name']
            xg = round(team_data['xg'], 1)
            pts = round(team_data['pts'], 1)
            xPoints = round(team_data['xPoints'], 1)
            xPointsDiff = round(team_data['xPointsDiff'], 1)
            xPosition = round(team_data['xPosition'], 1)
            xPositionDiff = round(team_data['xPositionDiff'], 1)
            xgConceded = round(team_data['xgConceded'], 1)
            xgConcededDiff = round(team_data['xgConcededDiff'], 1)
            xgDiff = round(team_data['xgDiff'], 1)

            xg_list.append(
                {"rank": xPosition, "rank_diff": xPositionDiff, "team": team_name, "xG": xg, "xG_Diff": xgDiff,
                 "xGA": xgConceded, "xGA_Diff": xgConcededDiff, "x_pts": pts, "x_points": xPoints,
                 "x_points_diff": xPointsDiff})

            # Update max widths
            max_widths["rank"] = max(max_widths["rank"], len(str(xPosition)))
            max_widths["rank_diff"] = max(max_widths["rank_diff"], len(str(xPositionDiff)))
            max_widths["team"] = max(max_widths["team"], len(team_name))
            max_widths["xG"] = max(max_widths["xG"], len(str(xg)))
            max_widths["xG_Diff"] = max(max_widths["xG_Diff"], len(str(xgDiff)))
            max_widths["xGA"] = max(max_widths["xGA"], len(str(xgConceded)))
            max_widths["xGA_Diff"] = max(max_widths["xGA_Diff"], len(str(xgConcededDiff)))
            max_widths["x_pts"] = max(max_widths["x_pts"], len(str(pts)))
            max_widths["x_points"] = max(max_widths["x_points"], len(str(xPoints)))
            max_widths["x_points_diff"] = max(max_widths["x_points_diff"], len(str(xPointsDiff)))

        # Print header
        header = f"{'排名':<{max_widths['rank']}}  {'排名变化':<{max_widths['rank_diff']}}  {'球队':<{max_widths['team']}}  {'xG':<{max_widths['xG']}}  {'xGDiff':<{max_widths['xG_Diff']}}  {'xGA':<{max_widths['xGA']}}  {'xGADiff':<{max_widths['xGA_Diff']}}  {'积分':<{max_widths['x_pts']}}  {'xPoints':<{max_widths['x_points']}}  {'xPointsDiff':<{max_widths['x_points_diff']}}"
        print(header)
        print("-" * len(header))

        # Print data
        for team_data in xg_list:
            print(
                f"{team_data['rank']:<{max_widths['rank']}}  {colorize_value(team_data['rank_diff']):<{max_widths['rank_diff']}}  {team_data['team']:<{max_widths['team']}}  {team_data['xG']:<{max_widths['xG']}}  {colorize_value(team_data['xG_Diff']):<{max_widths['xG_Diff']}}  {team_data['xGA']:<{max_widths['xGA']}}  {colorize_value(team_data['xGA_Diff']):<{max_widths['xGA_Diff']}}  {team_data['x_pts']:<{max_widths['x_pts']}}  {team_data['x_points']:<{max_widths['x_points']}}  {colorize_value(team_data['x_points_diff']):<{max_widths['x_points_diff']}}"
            )

        xg_df = pd.DataFrame(xg_list)
        xg_df.to_csv("xg.csv", index=False)

    except Exception as e:
        logger.error(f"获取XG数据失败，错误信息：{e}")


get_xg_data()
