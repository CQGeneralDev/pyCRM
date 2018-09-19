# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: CurrentSession
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/7 11:02
@Description:
-------------------------------------------------
@Change Activity:
    2018/9/7:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

from pyCRM.AuxiliaryTools.RedisData import RedisDict
from pyCRM import main_config


class UserSession(RedisDict):
    def __init__(self, user_id, session_id):
        args = main_config['session']
        super(UserSession, self).__init__(session_id, **args)
        super(UserSession, self).__setitem__('id', user_id)
