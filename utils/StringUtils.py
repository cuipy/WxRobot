#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import random
import hashlib

# 生成随机字符串
def buildRandom(dateFormat="%y%m%d%H%M%S",randLen = 6):
    rndmax = pow(10,(randLen)) - 1
    rndmin = pow(10,randLen-1)

    strRnd = random.randint(rndmin,rndmax)
    strTime = time.strftime(dateFormat, time.localtime())

    return "%s%s"%(strTime,strRnd)

# md5加密
def md5(bs):
    if not bs or not isinstance(bs,bytes) :
        print('md5 param 0 must bytes.')
        return False
    m5 = hashlib.md5()
    m5.update( bs )
    return m5.hexdigest()

# 汉字进行quote转码
def hanzi_quote(str):
    from urllib import parse
    return parse.quote(str)
