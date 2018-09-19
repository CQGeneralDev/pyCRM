# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: RedisData
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/17 11:11
@Description: 一些python常用的数据类型到redis的映射
-------------------------------------------------
@Change Activity:
    2018/9/17:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

import redis
import time

redis_pool_list = dict()


def get_redis_conn_pool(host, port, db, password, max_conn):
    redis_server_info = '%s_%d_%d' % (host, port, db)
    pool = redis_pool_list.get(redis_server_info)
    if pool is not None and isinstance(pool, redis.ConnectionPool):
        return pool
    redis_pool_list[redis_server_info] = redis.ConnectionPool(host=host, port=port, db=db, password=password,
                                                              max_connections=max_conn)
    return redis_pool_list[redis_server_info]


class RedisDict(object):
    def __init__(self, obj_id, redis_ip='127.0.0.1', redis_port=6379, redis_db=0, redis_pass=None, max_conn=10,
                 clean=False, time_out=0):
        self.__redis_pool = get_redis_conn_pool(redis_ip, redis_port, redis_db, redis_pass, max_conn)
        self.__id = obj_id
        self.__timeout = time_out
        redis_conn = redis.Redis(connection_pool=self.__redis_pool)
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
        redis_conn = redis.Redis(connection_pool=self.__redis_pool)
        assert redis_conn.exists(self.__id)
        return redis_conn.hget(self.__id, item)

    def __delitem__(self, key):
        redis_conn = redis.Redis(connection_pool=self.__redis_pool)
        assert redis_conn.exists(self.__id)
        redis_conn.hdel(self.__id, key)

    def __setitem__(self, key, value):
        if key == 'start_time':
            return
        redis_conn = redis.Redis(connection_pool=self.__redis_pool)
        assert redis_conn.exists(self.__id)
        redis_conn.hset(self.__id, key, value)
        redis_conn.hset(self.__id, 'last_change', time.time())

    def keys(self):
        redis_conn = redis.Redis(connection_pool=self.__redis_pool)
        assert redis_conn.exists(self.__id)
        return redis_conn.hkeys(self.__id)

    def clear(self):
        redis_conn = redis.Redis(connection_pool=self.__redis_pool)
        assert redis_conn.exists(self.__id)
        redis_conn.delete(self.__id)
        self.__create_dict(redis_conn, self.__timeout)

    def get_id(self):
        return self.__id


class RedisList(list):
    pass
