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
import json
import traceback

from datetime import datetime
from sqlalchemy import Column, SmallInteger, String, Text, UnicodeText, DateTime, Boolean, Unicode, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

from pyCRM import data_conn
from pyCRM import Session
from pyCRM import logger
from pyCRM.Security import get_algorithm
from pyCRM.Error import insert_error_wapper

Base = declarative_base()


class UserAuth(Base):
    """
    用户安全表,存放用户账号密码
    securityId:ID
    loginName:登陆账号
    loginPassword:登陆密码
    loginCount:登陆次数
    isActive:是否为活跃账号
    passwordAlgorithm:密码加密算法
    createDate:创建时间
    lastLoginTime:最后登陆时间
    """
    __tablename__ = 'UserAuth'
    securityId = Column(String(36), primary_key=True, default=lambda: ''.join(str(uuid.uuid1()).split('-')))
    loginName = Column(String(255), nullable=False, unique=True, index=True)
    loginPassword = Column(String(1024), nullable=False)
    userSession = Column(Text)
    passwordAlgorithm = Column(SmallInteger, default=0, nullable=False)
    loginCount = Column(SmallInteger, default=0, nullable=False)
    isActive = Column(Boolean, default=True)
    createDate = Column(TIMESTAMP, default=datetime.now)
    lastLoginTime = Column(TIMESTAMP)


class UserSession(Base):
    """
    用户session表
    sessionID:用户session id
    userID:用户id
    sessionText:session具体内容,保存为json格式
    createDate:创建时间
    lastChangeTime:最后修改时间
    """
    __tablename__ = 'Session'
    sessionID = Column(String(36), primary_key=True, default=lambda: ''.join(str(uuid.uuid1()).split('-')))
    userID = Column(String(36), nullable=False, unique=True, index=True)
    sessionText = Column(Text)
    createDate = Column(TIMESTAMP, default=datetime.now)
    lastChangeTime = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)


Base.metadata.create_all(data_conn)


class UserSessionDao(object):
    """
    UserSession模型的Dao类
    用于UserSession模型的数据库处理
    包含有基本的增删改查
    """

    def __init__(self, user):
        """
        创建UserSessionDao
        :param user: 自定的user,必须为UserAuth类
        """
        self.__user = user

    @insert_error_wapper(30000, '创建用户session失败')
    def insert(self):
        """
        创建一个user session
        :return:session id,失败返回错误代码
        """
        user_session = UserSession()
        session = Session()
        try:
            user_session.userID = self.__user.securityId
            session.add(user_session)
            session.commit()
            return True, None
        except:
            logger.critical(traceback.format_exc())
            session.rollback()
            return False, 30000
        finally:
            session.close()

    @insert_error_wapper(30001, '删除用户session失败')
    def delete(self):
        """
        删除用户session
        :return: 失败返回错误代码
        """
        session = Session()
        try:
            session.query(UserSession).filter(UserSession.userID == self.__user.securityId).delete()
            session.commit()
            return True, None
        except:
            logger.critical(traceback.format_exc())
            session.rollback()
            return False, 30001
        finally:
            session.close()

    @insert_error_wapper(30002, '待修改session格式异常,非字典类型')
    @insert_error_wapper(30003, '修改用户session时数据库异常')
    def update(self, session_dict):
        """
        修改用户session
        :param session_dict:待修改的session的字典,此变量必须为python字典
        :return:失败返回错误代码
        """
        session = Session()
        try:
            if type(session_dict) != dict:
                return False, 30002
            user_session = session.query(UserSession).filter(UserSession.userID == self.__user.securityId).first()
            if user_session.sessionText is None:
                user_session.sessionText = json.dumps(session_dict)
            else:
                old_session_dict = json.loads(user_session.sessionText)
                old_session_dict.update(session_dict)
                user_session.sessionText = json.dumps(old_session_dict)
            user_session.lastChangeTime = datetime.now()
            session.commit()
            return True, None
        except:
            logger.critical(traceback.format_exc())
            session.rollback()
            return False, 30003
        finally:
            session.close()

    @insert_error_wapper(30004, '未查找到指定用户session')
    @insert_error_wapper(30005, '查询指定用户session时数据库错误')
    def select(self):
        """
        查询用户session
        :return: 成功返回(True,用户session)失败返回(False,错误代码)
        """
        session = Session()
        try:
            user_session = session.query(UserSession).filter(UserSession.userID == self.__user.securityId).first()
            if user_session is None:
                return False, 30004
            return True, user_session
        except:
            logger.critical(traceback.format_exc())
            return False, 30005
        finally:
            session.close()

    @insert_error_wapper(30006, '统计指定用户session时数据库错误')
    def count_user_session(self):
        session = Session()
        try:
            count = session.query(func.count(UserSession.sessionID)).filter(
                UserSession.userID == self.__user.securityId).scalar()
            return True, count
        except:
            logger.critical(traceback.format_exc())
            return False, 30006
        finally:
            session.close()


class UserAuthDao(object):
    """
    UserAuth模型的Dao类
    """

    def __init__(self, login_name=None, password='null', algorithm=1):
        """
        创建UserAuthDao
        :param login_name:用户登陆名
        :param password: 用户密码
        :param algorithm: 密码加密算法,注意创建用户后,加密算法不能更改,默认算法代码为1
        """
        self.__algorithm_id = algorithm
        self.__algorithm = get_algorithm(algorithm)
        self.login_name = login_name
        self.password_algorithm = algorithm
        self.login_password = self.__algorithm.encoding(password)

    @insert_error_wapper(10001, '创建用户时数据库异常')
    @insert_error_wapper(10000, '空的用户名')
    def insert(self):
        """
        创建新的用户登陆信息
        :return:成功返回True,失败返回False以及错误代码
        """
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
        """
        删除用户信息
        :return: 成功返回True,失败返回False以及错误代码
        """
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

        """
        修改用户信息
        :param kwargs:待修改用户登陆信息的键值对
        :return:成功返回True,失败返回False以及错误代码,注意:passwordAlgorithm,loginName,securityId这介个属性不能修改
        """
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
        """
        查询用户信息
        :return: 成功(True,用户登陆信息)失败(False,错误代码)
        """
        session = Session()
        try:
            user_auth = session.query(UserAuth).filter(UserAuth.loginName == self.login_name).first()
            if user_auth is None:
                return False, 10005
            return True, user_auth
        except:
            logger.critical(traceback.format_exc())
            return False, 10006
        finally:
            session.close()


class UserSessionService(object):
    """
        UserSession模型的Service类
        """

    @staticmethod
    def check_user_has_session(username):
        """
        查询用户session
        :param username:用户名
        :return: session数量
        """
        user_auth_dao = UserAuthDao(login_name=username)
        user_auth = user_auth_dao.select()
        if user_auth[0]:
            user_auth = user_auth[1]
            user_session_dao = UserSessionDao(user_auth)
            return user_session_dao.count_user_session()
        else:
            return False, 40000

    @staticmethod
    @insert_error_wapper(40000, '查询用户信息失败')
    def create_user_session(username):
        """
        创建用户session
        :param username:用户名
        :return:成功返回(True,sessionId)失败返回(False,错误代码)
        """
        user_auth_dao = UserAuthDao(login_name=username)
        user_auth = user_auth_dao.select()
        if user_auth[0]:
            user_auth = user_auth[1]
            user_session_dao = UserSessionDao(user_auth)
            user_session_dao.insert()
            return user_session_dao.select()
        else:
            return False, 40000

    @staticmethod
    def delete_user_session(username):
        """
        删除用户session
        :param username:指定用户名
        :return:成功返回(True,None)失败返回(False,错误代码)
        """
        user_auth_dao = UserAuthDao(login_name=username)
        user_auth = user_auth_dao.select()
        if user_auth[0]:
            user_auth = user_auth[1]
            user_session_dao = UserSessionDao(user_auth)
            return user_session_dao.delete()
        else:
            return False, 40000

    @staticmethod
    def update_user_session(username, session_dict):
        """
        修改session
        :param username:用户名
        :param session_dict: 待修改session的字典
        :return:成功返回(True,None)失败返回(False,错误代码)
        """
        user_auth_dao = UserAuthDao(login_name=username)
        user_auth = user_auth_dao.select()
        if user_auth[0]:
            user_auth = user_auth[1]
            user_session_dao = UserSessionDao(user_auth)
            return user_session_dao.update(session_dict)
        else:
            return False, 40000

    @staticmethod
    def get_user_session(username):
        """
        查询用户session
        :param username:用户名
        :return: 成功返回(True,用户session)失败返回(False,错误代码)
        """
        user_auth_dao = UserAuthDao(login_name=username)
        user_auth = user_auth_dao.select()
        if user_auth[0]:
            user_auth = user_auth[1]
            user_session_dao = UserSessionDao(user_auth)
            return user_session_dao.select()
        else:
            return False, 40000


class UserAuthService(object):
    """
    UserAuth模型的Service类
    """

    @staticmethod
    @insert_error_wapper(20000, '用户密码校验失败')
    @insert_error_wapper(20002, '用户被冻结')
    def password_check(username, password):
        """
        检查用户账号及密码
        注意:验证通过条件,用户未被冻结,用户账号密码与数据库中的数据一致
        :param username:用户登陆账号
        :param password:用户密码
        :return:验证通过返回True,失败返回False及错误代码
        """
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
        """
        修改用户密码
        :param username:用户名
        :param new_password:用户新密码
        :return:成功返回True,失败返回False,错误代码
        """
        user = UserAuthDao(username)
        result = user.update(loginPassword=new_password)
        if result[0]:
            return True, '修改用户密码成功'
        return False, 20001

    @staticmethod
    @insert_error_wapper(20002, '冻结用户失败')
    def frozen_user(username):
        """
        冻结用户
        :param username:用户名
        :return:
        """
        user = UserAuthDao(username)
        result = user.update(isActive=False)
        if result[0]:
            return True, '冻结用户成功'
        return False, 20002

    @staticmethod
    @insert_error_wapper(20002, '解冻冻结用户失败')
    def unfrozen_user(username):
        """
        解冻用户
        :param username:用户名
        :return:
        """
        user = UserAuthDao(username)
        result = user.update(isActive=True)
        if result[0]:
            return True, '解冻用户成功'
        return False, 20002

    @staticmethod
    @insert_error_wapper(20003, '删除用户失败')
    def delete_user(username):
        """
        删除用户
        :param username:用户名
        :return:
        """
        user = UserAuthDao(username)
        result = user.delete()
        if result[0]:
            return True, '删除用户成功'
        return False, 20003

    @staticmethod
    @insert_error_wapper(20004, '创建用户失败')
    def create_user(username, password):
        """
        创建用户登陆信息
        :param username: 用户登陆账号
        :param password: 用户登陆密码
        :return: 成功返回True,失败返回False以及错误代码
        """
        user = UserAuthDao(username, password)
        result = user.insert()
        if result[0]:
            return True, '创建用户成功'
        return False, 20004

    @staticmethod
    def get_user(username):
        user = UserAuthDao(login_name=username)
        return user.select()


class AuthenticationDao(object):
    def __init__(self, username, password):
        self.__username = username
        self.__password = password

    @insert_error_wapper(50000, '用户不存在')
    @insert_error_wapper(50001, '密码检测错误')
    @insert_error_wapper(50002, '用户以登陆')
    def login(self):
        """
        用户登陆并创建session
        会检查用户密码以及用户是否已登陆
        :return:
        """
        session = Session()
        try:
            user_auth = session.query(UserAuth).filter(UserAuth.loginName == self.__username).first()
            if user_auth is None:
                return False, 50000
            algorithm = get_algorithm(user_auth.passwordAlgorithm)
            if not algorithm.check(self.__password, user_auth.loginPassword):
                return False, 50001
            count = session.query(func.count(UserSession.sessionID)).filter(
                UserSession.userID == user_auth.securityId).scalar()
            if count is None or count == 0:
                pass
            else:
                return False, 50002
            user_session = UserSession()
            user_session.userID = user_auth.securityId
            session.add(user_session)
            if user_auth.userSession is not None:
                user_session.sessionText = user_auth.userSession
            session.commit()
            return True, user_session.sessionID
        except:
            logger.critical(traceback.format_exc())
            session.rollback()
            return False, 10005
        finally:
            session.close()


class AuthenticationBackTask(object):
    """
    Authentication后台处理类
    主要用于一些数据库的后台任务,例如超时删除等等
    """
    pass


if __name__ == '__main__':
    # UserSessionService.create_user_session('gao')
    print(UserSessionService.update_user_session('gao', {'aaa': 44, 'bbb': 'ccc', 'ww': 2223}))
    # user=UserAuthDao('gao')
    # print(user.select())
