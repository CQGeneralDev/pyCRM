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

import traceback

from pyCRM import Session
from pyCRM import logger

from pyCRM.HumanResourceManagement.models.UserInfo import User
from pyCRM.HumanResourceManagement.models.UserInfo import UserDelete

from pyCRM.AuxiliaryTools.Security import get_algorithm
from pyCRM.AuxiliaryTools.Error import insert_error_wapper


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
