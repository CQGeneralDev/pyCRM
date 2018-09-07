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

import uuid
import time
import redis

from pyCRM import redis_poll
from pyCRM import main_config


class UserSession(dict):
    def __init__(self, user_id):
        self.user_id = user_id
        self.session_id = None
        super(UserSession, self).__init__()
        self.__create_session()
        self.__check_timeout()

    def __check_timeout(self):
        if time.time() - float(self['last_change_time']) >= main_config['session']['time_out']:
            redis_conn = redis.Redis(connection_pool=redis_poll)
            redis_conn.delete(self.user_id + '_' + self.session_id)
            self.clear()
            self.__create_session()

    def __create_session(self):
        redis_conn = redis.Redis(connection_pool=redis_poll)
        session_list = redis_conn.keys(pattern=self.user_id + '*')
        if len(session_list) == 0:
            self.session_id = ''.join(str(uuid.uuid1()).split('-'))
            redis_conn.hset(self.user_id + '_' + self.session_id, 'start_time', time.time())
            redis_conn.hset(self.user_id + '_' + self.session_id, 'last_change_time', time.time())
        else:
            self.session_id = session_list[0].split('_')[1]
        for key in redis_conn.hkeys(self.user_id + '_' + self.session_id):
            super(UserSession, self).__setitem__(key, redis_conn.hget(self.user_id + '_' + self.session_id, key))
        redis_conn.expire(self.user_id + '_' + self.session_id, main_config['session']['time_out'] * 5)

    def __setitem__(self, key, value):
        t = time.time()
        if key == 'start_time':
            return
        redis_conn = redis.Redis(connection_pool=redis_poll)
        assert redis_conn.exists(self.user_id + '_' + self.session_id)
        redis_conn.hset(self.user_id + '_' + self.session_id, key, value)
        redis_conn.hset(self.user_id + '_' + self.session_id, 'last_change_time', t)
        super(UserSession, self).__setitem__(key, value)
        super(UserSession, self).__setitem__('last_change_time', t)
        redis_conn.expire(self.user_id + '_' + self.session_id, main_config['session']['time_out'] * 5)

    def __delitem__(self, key):
        if key == 'start_time' or key == 'last_change_time':
            return
        t = time.time()
        redis_conn = redis.Redis(connection_pool=redis_poll)
        assert redis_conn.exists(self.user_id + '_' + self.session_id)
        redis_conn.hdel(self.user_id + '_' + self.session_id, key)
        super(UserSession, self).__delitem__(key)
        redis_conn.hset(self.user_id + '_' + self.session_id, 'last_change_time', t)
        super(UserSession, self).__setitem__('last_change_time', t)
        redis_conn.expire(self.user_id + '_' + self.session_id, main_config['session']['time_out'] * 5)

    def __getitem__(self, item):
        redis_conn = redis.Redis(connection_pool=redis_poll)
        assert redis_conn.exists(self.user_id + '_' + self.session_id)
        return super(UserSession, self).__getitem__(item)

    def clear(self):
        redis_conn = redis.Redis(connection_pool=redis_poll)
        assert redis_conn.exists(self.user_id + '_' + self.session_id)
        keys = list(self.keys())
        for key in keys:
            del self[key]
