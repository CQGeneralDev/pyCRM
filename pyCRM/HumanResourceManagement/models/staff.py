# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: staff
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/3 22:13
@Description: 用于员工的信息模型
-------------------------------------------------
@Change Activity:
    2018/9/3:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

import uuid
from datetime import datetime

from sqlalchemy import Column, SmallInteger, String, Text, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StaffInfo(Base):
    __tablename__ = 'staff'
    staffId = Column(String(36), primary_key=True, default=lambda: ''.join(str(uuid.uuid1()).split('-')))
    loginName = Column(String(255), nullable=False, unique=True, index=True)
    loginPassword = Column(String(1024), nullable=False)
    userSession = Column(Text)
    passwordAlgorithm = Column(SmallInteger, default=0, nullable=False)
    loginCount = Column(SmallInteger, default=0, nullable=False)
    isActive = Column(Boolean, default=True)
    createDate = Column(TIMESTAMP, default=datetime.now)
    lastLoginTime = Column(TIMESTAMP)
