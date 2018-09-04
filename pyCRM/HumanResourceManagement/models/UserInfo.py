# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: UserInfo
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/3 22:13
@Description: 用于系统用户的信息模型
-------------------------------------------------
@Change Activity:
    2018/9/3:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

import json
import uuid

from datetime import datetime

from pyCRM import data_conn
from pyCRM import module_to_dict

from pyCRM.AuxiliaryTools import DateEncoder

from sqlalchemy import Column, SmallInteger, String, Text, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    用户表
    userID:ID
    loginName:登陆账号
    loginPassword:登陆密码
    userConfig:用户配置信息
    userInfo:用户其他信息
    loginCount:登陆次数
    isActive:是否为活跃账号
    passwordAlgorithm:密码加密算法
    createDate:创建时间
    lastChangeTime:最后修改时间
    lastLoginTime:最后登陆时间
    """
    __tablename__ = 'user'
    userID = Column(String(36), primary_key=True, default=lambda: ''.join(str(uuid.uuid1()).split('-')))
    loginName = Column(String(255), nullable=False, unique=True, index=True)
    loginPassword = Column(String(1024), nullable=False)
    userSession = Column(Text)
    userInfo = Column(Text)
    passwordAlgorithm = Column(SmallInteger, default=0, nullable=False)
    loginCount = Column(SmallInteger, default=0, nullable=False)
    isActive = Column(Boolean, default=False)
    createDate = Column(TIMESTAMP, default=datetime.now)
    lastChangeTime = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    lastLoginTime = Column(TIMESTAMP)

    def __str__(self):
        return json.dumps(module_to_dict(User, self), cls=DateEncoder)


class UserDelete(Base):
    __tablename__ = 'user_delete'
    deleteID = Column(String(36), primary_key=True, default=lambda: ''.join(str(uuid.uuid1()).split('-')))
    deleteData = Column(Text, nullable=False)
    deleteDate = Column(TIMESTAMP, default=datetime.now)

    def __str__(self):
        return json.dumps(module_to_dict(UserDelete, self), cls=DateEncoder)


Base.metadata.create_all(data_conn)
