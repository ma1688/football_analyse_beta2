# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :logger.py
# @Time      :2024/7/23 下午10:50
# @Author    :MA-X-J
# @Software  :PyCharm
# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :logger.py
# @Time      :2024/7/23 下午10:31
# @Author    :MA-X-J
# @Software  :PyCharm
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :logger.py
# @Time      :2024/7/23 下午10:50
# @Author    :MA-X-J
# @Software  :PyCharm

import logging
import os
import sys

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FMT = "%Y-%m-%d %H:%M:%S %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s"
DEFAULT_LOG_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_FILENAME = "run.log"

# 设置日志路径为 ./data/log/run.log
LOG_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'log')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE_PATH = os.path.join(LOG_DIR, DEFAULT_LOG_FILENAME)


class Logger:
    def __init__(self):
        self._logger = logging.getLogger()
        if not self._logger.handlers:
            self.formatter = logging.Formatter(fmt=DEFAULT_LOG_FMT, datefmt=DEFAULT_LOG_DATETIME_FORMAT)
            self._logger.addHandler(self._get_console_handler())
            self._logger.addHandler(self._get_file_handler(filename=LOG_FILE_PATH))
            self._logger.setLevel(DEFAULT_LOG_LEVEL)

        # if python's version is 2, disable requests output info level log
        if sys.version_info.major == 2:
            logging.getLogger("requests").setLevel(logging.WARNING)

    def _get_file_handler(self, filename):
        """返回一个文件日志handler"""
        file_handler = logging.FileHandler(filename=filename, encoding="utf8")
        file_handler.setFormatter(self.formatter)
        return file_handler

    def _get_console_handler(self):
        """返回一个输出到终端日志handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        return console_handler

    @property
    def logger(self):
        return self._logger


logger = Logger().logger

