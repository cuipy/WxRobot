#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()

class WxFriend(Base):
    __tablename__='t_wx_friend'
    noid = Column(type_=INT, primary_key=True, autoincrement=True)
    puid = Column(type_=VARCHAR(32))
    frd_name = Column(type_=VARCHAR(32))
    frd_avatar = Column(type_=VARCHAR(64))


class WxGroup(Base):
    __tablename__='t_proxy_rule'
    noid = Column(type_=Integer, primary_key=True, autoincrement=True)
    puid = Column(type_=VARCHAR(32))
    frd_name = Column(type_=VARCHAR(32))
    frd_avatar = Column(type_=VARCHAR(64))
    owner_puid = Column(type_=VARCHAR(32))
    owner_name = Column(type_=VARCHAR(32))


