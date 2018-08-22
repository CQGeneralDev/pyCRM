# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: Authentication
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/8/22 10:09
@Description: 用于用户认证,以及用户session的处理
-------------------------------------------------
@Change Activity:
    2018/8/22:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

import uuid
import traceback

from datetime import datetime
from sqlalchemy import Column, SmallInteger, String, Text, UnicodeText, DateTime, Boolean, Unicode, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

from pyCRM import data_conn
from pyCRM import Session
from pyCRM.Security import get_algorithm

Base = declarative_base()


class UserAuth(Base):
    __tablename__ = 'UserAuth'
    securityId = Column(String(36), primary_key=True, default=lambda: ''.join(str(uuid.uuid1()).split('-')))
    loginName = Column(String(255), nullable=False, unique=True, index=True)
    loginPassword = Column(String(1024), nullable=False)
    passwordAlgorithm = Column(SmallInteger, default=0, nullable=False)
    loginCount = Column(SmallInteger, default=0, nullable=False)
    isActive = Column(Boolean, default=True)
    createDate = Column(TIMESTAMP, default=datetime.now)


Base.metadata.create_all(data_conn)


class UserAuthDao(object):
    def __init__(self, algorithm=1):
        self.__algorithm_id = algorithm
        self.__algorithm = get_algorithm(algorithm)

    def save(self, username, password):
        user_auth = UserAuth()
        user_auth.loginName = username
        user_auth.loginPassword = self.__algorithm.encoding(password)
        user_auth.passwordAlgorithm = self.__algorithm_id
        session = Session()
        try:
            session.add(user_auth)
            session.commit()
            return True, user_auth
        except:
            traceback.print_exc()
            session.rollback()
            return False, traceback.format_exc()
        finally:
            session.close()


class UserAuthService(object):
    pass


if __name__ == '__main__':
    userAuthDao = UserAuthDao()
    print(userAuthDao.save('gao', '123')[1])
