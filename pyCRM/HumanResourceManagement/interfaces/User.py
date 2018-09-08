# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: User
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/8 21:15
@Description: 
-------------------------------------------------
@Change Activity:
    2018/9/8:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

from pyCRM.AuxiliaryTools.Error import insert_error_wapper

from pyCRM.HumanResourceManagement.controller.service.UserService import check_user_password


@insert_error_wapper(1000000, '验证用户密码错误')
def login(username, password):
    if not check_user_password(username, password)[1]:
        return False, 1000000
