# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: Interfaces
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/8/27 16:05
@Description:
-------------------------------------------------
@Change Activity:
    2018/8/27:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

from functools import wraps

from jsonrpcserver import methods


def add(method):
    """
    将方法加入json rpc待调用方法列表
    :param method:待调用方法
    :return:
    """
    methods.add(method)

    @wraps(method)
    def wapper(*args, **kwargs):
        return method(*args, **kwargs)

    return wapper


def run(json_str):
    """
    运行json rpc方法
    :param json_str:json rpc字符串
    :return: 返回运行结果
    """
    return methods.dispatch(json_str)
