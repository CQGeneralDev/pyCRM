# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: UserDao
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/4 10:08
@Description:
-------------------------------------------------
@Change Activity:
    2018/9/4:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

import json
import traceback

from pyCRM import Session
from pyCRM import logger
from pyCRM.AuxiliaryTools.Error import insert_error_wapper
from pyCRM.AuxiliaryTools.Security import get_algorithm
from pyCRM.HumanResourceManagement.models.UserInfo import User
from pyCRM.HumanResourceManagement.models.UserInfo import UserDelete


@insert_error_wapper(100001, '创建用户时数据库异常')
@insert_error_wapper(100000, '空的用户名')
def insert_user(login_name, password, algorithm=1):
    """
    创建用户,拥有基本的信息,包括有账号密码
    但是用户默认被冻结,应为其他的信息不全
    必要信息包含有:用户名,证件类型,证件号码等等
    :param login_name:用户账号
    :param password:用户密码
    :param algorithm:用户密码加密方式
    :return:
    """
    user = User()
    user.loginName = login_name
    user.loginPassword = get_algorithm(algorithm).encoding(password)
    user.passwordAlgorithm = algorithm
    session = Session()
    if user.loginName is None:
        return False, 100000
    try:
        session.add(user)
        session.commit()
        return True, None
    except:
        logger.critical(traceback.format_exc())
        session.rollback()
        return False, 100001
    finally:
        session.close()


@insert_error_wapper(100003, '删除用户时数据库异常')
def delete_user(user_id):
    """
    删除指定用户
    :param user_id: 用户id
    :return:
    """
    session = Session()
    try:
        user = session.query(User).filter(User.userID == user_id).first()
        user_delete = UserDelete()
        user_delete.deleteData = str(user)
        session.add(user_delete)
        session.query(User).filter(User.userID == user_id).delete()
        session.commit()
        return True, None
    except:
        logger.critical(traceback.format_exc())
        session.rollback()
        return False, 100003
    finally:
        session.close()


@insert_error_wapper(100005, '修改用户属性时数据库错误')
@insert_error_wapper(100004, '不允许修改的属性')
def update_user(user_id, **kwargs):
    """
    修改用户属性
    :param user_id:用户id
    :param kwargs: 用户属性键值对,注意不能修改账号名,用户id,加密算法
    :return:
    """
    session = Session()
    try:
        user = session.query(User).filter(User.userID == user_id).first()
        for key in kwargs.keys():
            if key == 'loginPassword':
                setattr(user, key, get_algorithm(user.passwordAlgorithm).encoding(kwargs[key]))
                continue
            if key == 'passwordAlgorithm' or key == 'loginName' or key == 'userID':
                session.rollback()
                return False, 100004
            setattr(user, key, kwargs[key])
        session.commit()
        return True, None
    except:
        logger.critical(traceback.format_exc())
        session.rollback()
        return False, 100005
    finally:
        session.close()


@insert_error_wapper(100005, '未查找到指定用户')
@insert_error_wapper(100006, '查询时数据库异常')
def select_user(user_id):
    session = Session()
    try:
        user = session.query(User).filter(User.userID == user_id).first()
        if user is None:
            return False, 100005
        return True, user
    except:
        logger.critical(traceback.format_exc())
        return False, 100006
    finally:
        session.close()


def select_user_by_name(login_name):
    session = Session()
    try:
        user = session.query(User).filter(User.loginName == login_name).first()
        if user is None:
            return False, 100005
        return True, user
    except:
        logger.critical(traceback.format_exc())
        return False, 100006
    finally:
        session.close()


@insert_error_wapper(100007, '修改用户配置时数据库错误')
def update_user_config(user_id, **kwargs):
    """
    修改用户配置
    :param user_id: 用户id
    :param kwargs: 修改用户配置的键值对
    :return:
    """
    session = Session()
    try:
        user = session.query(User).filter(User.userID == user_id).first()
        if user.userInfo is None:
            user.userInfo = json.dumps(kwargs)
        else:
            user_info = json.loads(user.userInfo)
            for key in kwargs.keys():
                user_info[key] = kwargs[key]
            user.userInfo = json.dumps(user_info)
        session.commit()
        return True, None
    except:
        logger.critical(traceback.format_exc())
        return False, 100007
    finally:
        session.close()


@insert_error_wapper(100009, '删除用户配置时数据库错误')
def delete_user_config(user_id, key):
    """
    删除用户配置
    :param user_id: 用户id
    :param key: 待删除的用户配置键
    :return:
    """
    session = Session()
    try:
        user = session.query(User).filter(User.userID == user_id).first()
        if user.userInfo is None:
            return True, None
        else:
            user_info = json.loads(user.userInfo)
            if key in user_info.keys():
                del user_info[key]
                user.userInfo = json.dumps(user_info)
                session.commit()
        return True, None
    except:
        logger.critical(traceback.format_exc())
        return False, 100009
    finally:
        session.close()


@insert_error_wapper(100010, '清空用户配置时数据库错误')
def clean_user_config(user_id):
    """
    清空用户配置
    :param user_id:
    :return:
    """
    session = Session()
    try:
        user = session.query(User).filter(User.userID == user_id).first()
        user.userInfo = None
        session.commit()
        return True, None
    except:
        logger.critical(traceback.format_exc())
        return False, 100010
    finally:
        session.close()


@insert_error_wapper(100008, '修改用户session时数据库错误')
def update_user_session(user_id, **kwargs):
    """
    修改用户session,主要用于session的永久保存
    :param user_id: 用户id
    :param kwargs: 用户session对
    :return:
    """
    session = Session()
    try:
        user = session.query(User).filter(User.userID == user_id).first()
        if user.userSession is None:
            user.userSession = json.dumps(kwargs)
        else:
            user_session = json.loads(user.userSession)
            for key in kwargs.keys():
                user_session[key] = kwargs[key]
            user.userInfo = json.dumps(user_session)
        session.commit()
        return True, None
    except:
        logger.critical(traceback.format_exc())
        return False, 100008
    finally:
        session.close()


@insert_error_wapper(100011, '删除用户session时数据库错误')
def delete_user_session(user_id, key):
    """
    删除指定用户session
    :param user_id: 用户id
    :param key: session key
    :return:
    """
    session = Session()
    try:
        user = session.query(User).filter(User.userID == user_id).first()
        if user.userSession is None:
            return True, None
        else:
            user_session = json.loads(user.userSession)
            if key in user_session.keys():
                del user_session[key]
                user.userSession = json.dumps(user_session)
                session.commit()
                return True, None
    except:
        logger.critical(traceback.format_exc())
        return False, 100011
    finally:
        session.close()


@insert_error_wapper(100012, '清空用户session时数据库错误')
def clean_user_session(user_id):
    """
    清空指定用户session
    :param user_id:用户id
    :return:
    """
    session = Session()
    try:
        user = session.query(User).filter(User.userID == user_id).first()
        user.userSession = None
        session.commit()
        return True, None
    except:
        logger.critical(traceback.format_exc())
        return False, 100012
    finally:
        session.close()
