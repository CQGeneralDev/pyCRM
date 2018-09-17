# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: RedisData
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/17 11:11
@Description:
-------------------------------------------------
@Change Activity:
    2018/9/17:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

import redis
import time


class RedisDict(object):
    def __init__(self, obj_id, redis_ip='127.0.0.1', redis_port=6379, redis_db=0, redis_pass=None, max_conn=10,
                 clean=False, time_out=0):
        self.__redis_poll = redis.ConnectionPool(host=redis_ip, port=redis_port, db=redis_db, password=redis_pass,
                                                 max_connections=max_conn)
        self.__id = obj_id
        self.__timeout = time_out
        redis_conn = redis.Redis(connection_pool=self.__redis_poll)
        if redis_conn.exists(self.__id):
            if clean:
                redis_conn.delete(self.__id)
                self.__create_dict(redis_conn, time_out)
        else:
            self.__create_dict(redis_conn, time_out)

    def __create_dict(self, redis_conn, time_out):
        redis_conn.hset(self.__id, 'start_time', time.time())
        redis_conn.hset(self.__id, 'last_change', time.time())
        if time_out > 0:
            redis_conn.expire(self.__id, time_out)

    def __getitem__(self, item):
        redis_conn = redis.Redis(connection_pool=self.__redis_poll)
        assert redis_conn.exists(self.__id)
        return redis_conn.hget(self.__id, item)

    def __delitem__(self, key):
        redis_conn = redis.Redis(connection_pool=self.__redis_poll)
        assert redis_conn.exists(self.__id)
        redis_conn.hdel(self.__id, key)

    def __setitem__(self, key, value):
        if key == 'start_time':
            return
        redis_conn = redis.Redis(connection_pool=self.__redis_poll)
        assert redis_conn.exists(self.__id)
        redis_conn.hset(self.__id, key, value)
        redis_conn.hset(self.__id, 'last_change', time.time())

    def keys(self):
        redis_conn = redis.Redis(connection_pool=self.__redis_poll)
        assert redis_conn.exists(self.__id)
        return redis_conn.hkeys(self.__id)

    def clean(self):
        redis_conn = redis.Redis(connection_pool=self.__redis_poll)
        assert redis_conn.exists(self.__id)
        redis_conn.delete(self.__id)
        self.__create_dict(redis_conn, self.__timeout)


class RedisList(list):
    pass
