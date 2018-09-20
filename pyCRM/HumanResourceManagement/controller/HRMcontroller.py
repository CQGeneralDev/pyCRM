# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: HRMcontroller
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/18 16:00
@Description:
-------------------------------------------------
@Change Activity:
    2018/9/18:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

import uuid

from pyCRM.AuxiliaryTools.Error import insert_error_wapper
from pyCRM.HumanResourceManagement.controller.service.UserService import check_user_password
from pyCRM.HumanResourceManagement.models.CurrentSession import UserSession


@insert_error_wapper(1000001, '认证错误')
def login(username, password):
    """
    登陆系统,需要账号密码,并且账号不能被冻结
    :param username:
    :param password:
    :return:
    """
    check = check_user_password(username, password)
    if check[0]:
        session = UserSession(check[1], 'session_id_' + ''.join(str(uuid.uuid1()).split('-')))
        return True, session.get_id()
    else:
        return False, 1000001
