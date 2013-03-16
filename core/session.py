#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

import uuid
import OpenSSL
from .models import redisConn

SESSION_COOKIE_NAME = "session_id"
SESSION_REDIS_KEY = "_si"


def generate_session_id():
    return "".join(str(uuid.UUID(bytes=OpenSSL.rand.bytes(16))).split("-"))


class Session():
    def __init__(self, requestHandler):
        self.requestHandler = requestHandler
        self.session_id = self.requestHandler.get_cookie(SESSION_COOKIE_NAME, None)
        if self.session_id:
            self.session_data = redisConn.hgetall(self._getRedisKey())
            if not self.session_data or \
                    not self.session_data.get("UA_md5") == self.requestHandler.get_UA_md5():
                self.destroy()
                self._createSession()
        else:
            self._createSession()

    def _getRedisKey(self):
        """
        根据session_id获得redis中的键值
        :return:
        """
        return "{0}{1}".format(SESSION_REDIS_KEY, self.session_id)

    def _createSession(self):
        self.session_id = generate_session_id()
        self.requestHandler.set_cookie(SESSION_COOKIE_NAME, self.session_id)
        self.session_data = {
            "UA_md5": self.requestHandler.get_UA_md5()
        }
        redisConn.hmset(self._getRedisKey(), self.session_data)
        redisConn.expire(self._getRedisKey(), 7200)

    def __getitem__(self, item):
        """
        获取session中的值，不存在返回None
        :param item:
        :return:
        """
        return self.session_data.get(item, None)

    def __setitem__(self, key, value):
        """
        设置session中的指
        :param key:
        :param value:
        :return:
        """
        self.session_data[key] = value
        redisConn.hset(self._getRedisKey(), key, value)
        return True

    def __delitem__(self, key):
        """
        删除session中某个键
        :param key:
        :return:
        """
        del self.session_data[key]
        redisConn.hdel(self._getRedisKey(), key)
        return True

    def destroy(self):
        """
        清除session
        """
        self.session_data.clear()
        self.requestHandler.clear_cookie(SESSION_COOKIE_NAME)