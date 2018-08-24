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
from pyCRM import logger
from pyCRM.Security import get_algorithm
from pyCRM.Error import insert_error_wapper

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
    lastLoginTime = Column(TIMESTAMP)


Base.metadata.create_all(data_conn)


class UserAuthDao(object):
    def __init__(self, login_name=None, password='null', algorithm=1):
        self.__algorithm_id = algorithm
        self.__algorithm = get_algorithm(algorithm)
        self.login_name = login_name
        self.password_algorithm = algorithm
        self.login_password = self.__algorithm.encoding(password)

    @insert_error_wapper(10001, '创建用户时数据库异常')
    @insert_error_wapper(10000, '空的用户名')
    def insert(self):
        user_auth = UserAuth()
        user_auth.loginName = self.login_name
        user_auth.loginPassword = self.login_password
        user_auth.passwordAlgorithm = self.password_algorithm
        if user_auth.loginName is None:
            return False, 10000
        session = Session()
        try:
            session.add(user_auth)
            session.commit()
            return True, None
        except:
            logger.critical(traceback.format_exc())
            session.rollback()
            return False, 10001
        finally:
            session.close()

    @insert_error_wapper(10003, '删除用户时数据库异常')
    def delete(self):
        session = Session()
        try:
            session.query(UserAuth).filter(UserAuth.loginName == self.login_name).delete()
            session.commit()
            return True, None
        except:
            logger.critical(traceback.format_exc())
            session.rollback()
            return False, 10003
        finally:
            session.close()

    @insert_error_wapper(10005, '修改用户属性时数据库错误')
    @insert_error_wapper(10004, '不允许修改的属性')
    def update(self, **kwargs):
        session = Session()
        try:
            user_auth = session.query(UserAuth).filter(UserAuth.loginName == self.login_name).first()
            for key in kwargs.keys():
                if key == 'loginPassword':
                    kwargs[key] = self.__algorithm.encoding(kwargs[key])
                if key == 'passwordAlgorithm' or key == 'loginName' or key == 'securityId':
                    session.rollback()
                    return False, 10004
                setattr(user_auth, key, kwargs[key])
            session.commit()
            return True, None
        except:
            logger.critical(traceback.format_exc())
            session.rollback()
            return False, 10005
        finally:
            session.close()

    @insert_error_wapper(10007, '查找用户时数据库异常')
    @insert_error_wapper(10006, '未查找到指定用户')
    def select(self):
        session = Session()
        try:
            user_auth = session.query(UserAuth).filter(UserAuth.loginName == self.login_name).first()
            if user_auth is None:
                return False, 10005
            return True, user_auth
        except:
            logger.critical(traceback.format_exc())
            session.rollback()
            return False, 10006
        finally:
            session.close()


class UserAuthService(object):

    @staticmethod
    @insert_error_wapper(20000, '用户密码校验失败')
    @insert_error_wapper(20002, '用户被冻结')
    def password_check(username, password):
        user = UserAuthDao(username, password)
        user = user.select()
        if user[0]:
            user = user[1]
            if user.isActive:
                algorithm = get_algorithm(user.passwordAlgorithm)
                return algorithm.check(password, user.loginPassword), None
            else:
                return False, 20002
        return False, 20000

    @staticmethod
    @insert_error_wapper(20001, '修改用户密码失败')
    def change_password(username, new_password):
        user = UserAuthDao(username)
        result = user.update(loginPassword=new_password)
        if result[0]:
            return True, '修改用户密码成功'
        return False, 20001

    @staticmethod
    @insert_error_wapper(20002, '冻结用户失败')
    def frozen_user(username):
        user = UserAuthDao(username)
        result = user.update(isActive=False)
        if result[0]:
            return True, '冻结用户成功'
        return False, 20002

    @staticmethod
    @insert_error_wapper(20002, '解冻冻结用户失败')
    def unfrozen_user(username):
        user = UserAuthDao(username)
        result = user.update(isActive=True)
        if result[0]:
            return True, '解冻用户成功'
        return False, 20002

    @staticmethod
    @insert_error_wapper(20003, '删除用户失败')
    def delete_user(username):
        user = UserAuthDao(username)
        result = user.delete()
        if result[0]:
            return True, '删除用户成功'
        return False, 20003

    @staticmethod
    @insert_error_wapper(20004, '创建用户失败')
    def create_user(username, password):
        user = UserAuthDao(username, password)
        result = user.insert()
        if result[0]:
            return True, '创建用户成功'
        return False, 20004


if __name__ == '__main__':
    UserAuthService.delete_user('gao')
    logger.info('aaaa')
