# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: Error
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/8/23 9:52
@Description:
-------------------------------------------------
@Change Activity:
    2018/8/23:创建文件
-------------------------------------------------
"""

__author__ = 'gao'

import traceback
from functools import wraps

from sqlalchemy import Column, BigInteger, Text
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

from pyCRM import Session
from pyCRM import data_conn

Base = declarative_base()


class ErrorMessage(Base):
    """
    错误信息,用于存放系统中的各种错误代码及错误详细信息
    @param errorID:错误代码
    @param message:错误信息
    """
    __tablename__ = 'ErrorMessage'
    errorID = Column(BigInteger, primary_key=True)
    message = Column(Text)


Base.metadata.create_all(data_conn)


class ErrorDao(object):
    def __init__(self, error_id=0, message='null'):
        self.error_message = ErrorMessage()
        self.error_message.errorID = error_id
        self.error_message.message = message

    def insert(self):
        session = Session()
        count = session.query(func.count('*')).filter(ErrorMessage.errorID == self.error_message.errorID).scalar()
        try:
            if count != 0:
                em = session.query(ErrorMessage).filter(ErrorMessage.errorID == self.error_message.errorID).first()
                em.message = self.error_message.message
                session.commit()
            else:
                session.add(self.error_message)
                session.commit()
            return True, self.error_message
        except:
            traceback.print_exc()
            session.rollback()
            return False, traceback.format_exc()
        finally:
            session.close()

    def get(self, error_id):
        session = Session()
        try:
            self.error_message = session.query(ErrorMessage).filter(ErrorMessage.errorID == error_id).first()
            return True, self.error_message
        except:
            traceback.print_exc()
            return False, traceback.format_exc()
        finally:
            session.close()


class ErrorService(object):
    @staticmethod
    def insert_error(error_id, message):
        error_dao = ErrorDao(error_id, message)
        return error_dao.insert()

    @staticmethod
    def get_error(error_id):
        error_dao = ErrorDao()
        return error_dao.get(error_id)


def insert_error_wapper(error_id, message='null'):
    ErrorService.insert_error(error_id, message)

    def method_wapper(method):
        @wraps(method)
        def wapper(*args, **kwargs):
            return method(*args, **kwargs)

        return wapper

    return method_wapper
