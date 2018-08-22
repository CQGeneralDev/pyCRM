# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: mycode.crm.Controller.Security
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018年4月18日 下午12:50:26
@Description:
-------------------------------------------------
@Change Activity:
    2018年4月18日
-------------------------------------------------
"""
__author__ = 'gao'

import hashlib
from abc import abstractclassmethod, ABCMeta

__instances = {}


def add_algorithm(aid):
    def algorithm(cls):
        global __instances
        if aid not in __instances.keys():
            __instances[aid] = cls
        return cls

    return algorithm


def get_algorithm(aid=0):
    algorithm_class = __instances.get(aid)
    if algorithm_class is None:
        return GeneralSecurity()
    return algorithm_class()


class AbstractSecurity(metaclass=ABCMeta):

    @abstractclassmethod
    def encoding(self, password):
        pass

    @abstractclassmethod
    def check(self, password, sec_password):
        pass


@add_algorithm(0)
class GeneralSecurity(AbstractSecurity):

    def encoding(self, password):
        return password

    def check(self, password, sec_password):
        return self.encoding(password) == sec_password


@add_algorithm(1)
class MD5Security(AbstractSecurity):

    def encoding(self, password):
        md5str = hashlib.md5()
        md5str.update(password.encode(encoding='utf-8'))
        return md5str.hexdigest()

    def check(self, password, sec_password):
        return self.encoding(password) == sec_password
