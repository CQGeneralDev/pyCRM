# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: __init__.py
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/3 21:36
@Description: 
-------------------------------------------------
@Change Activity:
    2018/9/3:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

import json
import datetime


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
        else:
            return json.JSONEncoder.default(self, obj)
