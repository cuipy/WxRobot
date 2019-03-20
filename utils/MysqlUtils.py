#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from utils import LogUtils
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# 加入日志
# 获取logger实例
logger = LogUtils.buildLog()

conn_str = None

echo = True
max_overflow = 0
pool_size = 5
pool_timeout = 30
pool_recycle = 300

MySQLEngine = None


# 获取一个session
def getSession(connStr=None):
    global MySQLEngine
    global conn_str

    if conn_str==None:
        if connStr != None:
            conn_str = connStr
        else:
            logger.warn('参数connStr is None ，getSession is failure.')
            return None

    if MySQLEngine == None:
        MySQLEngine = create_engine(conn_str, echo=echo, max_overflow=max_overflow, pool_size=pool_size,
                                    pool_timeout=pool_timeout, pool_recycle=pool_recycle)

    sessionFactory = sessionmaker(bind=MySQLEngine)
    session = scoped_session(sessionFactory)
    return session


def execute(sql, params=None, session=None,connStr=None,commit=False):
    global conn_str
    if conn_str==None and session==None:
        if connStr != None:
            conn_str = connStr
        else:
            logger.warn('参数connStr is None ，getSession is failure.')
            return None

    needRemove = False
    if session == None:
        try:
            session = getSession(conn_str)
        except:
            logger.error('get session exception: %s' % (traceback.format_exc()))
            return False

        needRemove = True
    try:
        res = session.execute(sql, params=params)
    except:
        logger.error('execute sql %s error: %s' % (sql,traceback.format_exc()))
        return False

    if commit:
        session.commit()

    if needRemove:
        session.commit()
        session.remove()

    return res.rowcount

# 返回值类型为数组，每个元素为元祖，例如 [(1,'ok'),(2,'failure')]
def query(sql, params=None, session=None, connStr=None):
    global conn_str
    if conn_str == None and session==None:
        if connStr != None:
            conn_str = connStr
        else:
            logger.warn('参数connStr is None ，getSession is failure.')
            return None

    needRemove = False
    if session == None:
        try:
            session = getSession(conn_str)
        except:
            logger.error('get session exception: %s' % (traceback.format_exc()))
            return False

        needRemove = True

    resproxy = session.execute(sql, params=params)
    rows = resproxy.fetchall()

    if needRemove:
        session.commit()
        session.remove()

    return rows


# 返回格式为一个元祖 例如：(1,'ok')
def find(sql, params=None, session=None,connStr=None):
    global conn_str
    if conn_str == None and session==None:
        if connStr != None:
            conn_str = connStr
        else:
            logger.warn('参数connStr is None ，getSession is failure.')
            return None

    needRemove = False
    if session == None:
        try:
            session = getSession()
        except:
            logger.error('get session exception: %s' % (traceback.format_exc()))
            return False

        needRemove = True

    resproxy = session.execute(sql, params=params)
    rows = resproxy.fetchone()

    if needRemove:
        session.commit()
        session.remove()

    return rows
