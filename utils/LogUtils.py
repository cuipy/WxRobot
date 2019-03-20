#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import sys
import os

logger = None
def buildLog(logName = 'Logger' , level = logging.INFO, filePath = 'logs/test.log', format = '%(asctime)s  %(levelname)-8s:%(message)s'):
    global logger

    if logger != None:
        return logger

    logger = logging.getLogger( logName )

    logPath = filePath[0:filePath.rindex('/')];
    if not os.path.exists(logPath):
        os.makedirs(logPath)

    # 指定输出格式
    formatter = logging.Formatter(format)
    # 文件日志
    file_handler = logging.FileHandler(filePath)
    file_handler.setFormatter(formatter)
    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    sqlHandler = logging.FileHandler('logs/sqlalchemy.engine.log')  # 可以给它添加一个日志文件处理类
    sqlHandler.level = logging.DEBUG
    logging.getLogger('sqlalchemy.engine').addHandler(sqlHandler)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.setLevel(level=level)

    return logger



