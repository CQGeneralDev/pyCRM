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
    def __init__(self, login_name=None, password='null', algorithm=1):
        self.__algorithm_id = algorithm
        self.__algorithm = get_algorithm(algorithm)
        self.login_name = login_name
        self.password_algorithm = algorithm
        self.login_password = self.__algorithm.encoding(password)

    def insert(self):
        user_auth = UserAuth()
        user_auth.loginName = self.login_name
        user_auth.loginPassword = self.login_password
        user_auth.passwordAlgorithm = self.password_algorithm
        if user_auth.loginName is None:
            return False, None
        session = Session()
        try:
            session.add(user_auth)
            session.commit()
            return True, None
        except:
            traceback.print_exc()
            session.rollback()
            return False, traceback.format_exc()
        finally:
            session.close()

    def delete(self):
        session = Session()
        try:
            session.query(UserAuth).filter(UserAuth.loginName == self.login_name).delete()
            session.commit()
            return True, None
        except:
            traceback.print_exc()
            session.rollback()
            return False, traceback.format_exc()
        finally:
            session.close()

    def update(self, **kwargs):
        session = Session()
        try:
            user_auth = session.query(UserAuth).filter(UserAuth.loginName == self.login_name).first()
            for key in kwargs.keys():
                if key == 'loginPassword':
                    kwargs[key] = self.__algorithm.encoding(kwargs[key])
                if key == 'passwordAlgorithm' or key == 'loginName' or key == 'securityId':
                    raise Exception('不允许修改的属性')
                setattr(user_auth, key, kwargs[key])
            session.commit()
            return True, None
        except:
            traceback.print_exc()
            session.rollback()
            return False, traceback.format_exc()
        finally:
            session.close()

    def select(self):
        session = Session()
        try:
            user_auth = session.query(UserAuth).filter(UserAuth.loginName == self.login_name).first()
            return True, user_auth
        except:
            traceback.print_exc()
            session.rollback()
            return False, traceback.format_exc()
        finally:
            session.close()


class UserAuthService(object):
    def login(self, username, password):
        pass


if __name__ == '__main__':
    userAuthDao = UserAuthDao('aaaa', '123')
    print(userAuthDao.select()[1].createDate)
