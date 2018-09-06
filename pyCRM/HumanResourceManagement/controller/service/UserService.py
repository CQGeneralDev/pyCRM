# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: UserService
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/4 14:32
@Description:
-------------------------------------------------
@Change Activity:
    2018/9/4:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

import json

from pyCRM import main_config
from pyCRM.AuxiliaryTools.Error import insert_error_wapper
from pyCRM.HumanResourceManagement.controller.dao.UserDao import clean_user_config as clean_user_config_id
from pyCRM.HumanResourceManagement.controller.dao.UserDao import clean_user_session as clean_user_session_id
from pyCRM.HumanResourceManagement.controller.dao.UserDao import delete_user as d_user
from pyCRM.HumanResourceManagement.controller.dao.UserDao import delete_user_config as delete_user_config_id
from pyCRM.HumanResourceManagement.controller.dao.UserDao import delete_user_session as delete_user_session_id
from pyCRM.HumanResourceManagement.controller.dao.UserDao import insert_user
from pyCRM.HumanResourceManagement.controller.dao.UserDao import select_user
from pyCRM.HumanResourceManagement.controller.dao.UserDao import select_user_by_name
from pyCRM.HumanResourceManagement.controller.dao.UserDao import update_user
from pyCRM.HumanResourceManagement.controller.dao.UserDao import update_user_config
from pyCRM.HumanResourceManagement.controller.dao.UserDao import update_user_session as update_user_session_id


@insert_error_wapper(200000, '创建新用户失败')
def create_user(username, password, algorithm=1, **kwargs):
    """
    创建用户
    :param username: 用户名
    :param password: 用户密码
    :param algorithm: 密码加密算法
    :param kwargs: 用户其他属性
    :return:
    """
    if not insert_user(username, password, algorithm)[0]:
        return False, 200000
    user = select_user_by_name(username)
    if not user[0]:
        return user
    user = user[1]
    if kwargs is not None:
        update_user(user.userID, userInfo=json.dumps(kwargs))
    return True, user.userID


@insert_error_wapper(200001, '缺少用户必要信息')
def activation_user_id(user_id):
    """
    激活用户,是用户可登陆
    :param user_id:用户id
    :return:
    """
    check_key = main_config['user']['check_key']
    user = select_user(user_id)
    if not user[0]:
        return user
    user = user[1]
    user_info = user.userInfo
    if user_info is None:
        return False, 200001
    user_info_dict = json.loads(user_info)
    for key in check_key:
        if key not in user_info_dict.keys():
            return False, 200001
    return update_user(user_id, isActive=True)


def activation_user(username):
    """
    激活用户
    :param username:用户名
    :return:
    """
    user = select_user_by_name(username)
    if not user[0]:
        return user
    return activation_user_id(user[1].userID)


def frozen_user_id(user_id):
    """
    冻结用户
    :param user_id:
    :return:
    """
    return update_user(user_id, isActive=False)


def frozen_user(username):
    """
    冻结用户
    :param username:
    :return:
    """
    user = select_user_by_name(username)
    if not user[0]:
        return user
    return frozen_user_id(user[1].userID)


def delete_user_id(user_id):
    return d_user(user_id)


def delete_user(username):
    user = select_user_by_name(username)
    if not user[0]:
        return user
    return delete_user_id(user[1].userID)


def set_user_config_id(user_id, **kwargs):
    return update_user_config(user_id, **kwargs)


def set_user_config(username, **kwargs):
    user = select_user_by_name(username)
    if not user[0]:
        return user
    return set_user_config_id(user[1].userID, **kwargs)


def delete_user_config(username, key):
    user = select_user_by_name(username)
    if not user[0]:
        return user
    return delete_user_config_id(user[1].userID, key)


def clean_user_config(username):
    user = select_user_by_name(username)
    if not user[0]:
        return user
    return clean_user_config_id(user[1].userID)


def update_user_session(username, **kwargs):
    user = select_user_by_name(username)
    if not user[0]:
        return user
    return update_user_session_id(user[1].userID, **kwargs)


def delete_user_session(username, key):
    user = select_user_by_name(username)
    if not user[0]:
        return user
    return delete_user_session_id(user[1].userID, key)


def clean_user_session(username):
    user = select_user_by_name(username)
    if not user[0]:
        return user
    return clean_user_session_id(user[1].userID)
