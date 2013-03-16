#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from core.web import BaseHandler
from .models import CCNUAuth


CLASS_KEY = "CuiLanQiao"


def loginDo(handler):
    if handler.get_current_user():
        handler.write("0")
        return True
    (email, password) = (
        handler.get_argument("email", None),
        handler.get_argument("password", None)
    )
    if handler.userHandler.login(email=email, password=password):
        handler.write("1")
        return True
    handler.write("0")


def logoutDo(handler):
    handler.userHandler.logout()
    handler.write("1")


def registerDo(handler):
    (email, ccnu_id, password, class_key) = (
        handler.get_argument("email", None),
        handler.get_argument("ccnu_id", None),
        handler.get_argument("password", None),
        handler.get_argument("class_key", None)
    )
    if not class_key == CLASS_KEY:
        handler.write("0")
        return True
    if not ccnu_id or not email or not len(ccnu_id) == 10 or not ccnu_id.isalnum() or not password:
        handler.write("0")
        return True
    info = CCNUAuth(ccnu_id, password, True)
    if not info:
        handler.write("0")
        return True
    if handler.userHandler.createUser(email=email, password=password, ccnu_id=ccnu_id, **info):
        handler.write("1")
        return True
    handler.write("0")


def restPasswordDo(handler):
    (ccnu_id, password) = (
        handler.get_argument("ccnu_id", None),
        handler.get_argument("password", None)
    )
    if not ccnu_id or not len(ccnu_id) == 10 or not ccnu_id.isalnum() or not password:
        handler.write("0")
        return True
    if not CCNUAuth(ccnu_id, password):
        handler.write("0")
        return True
    if handler.userHandler.setPassword(ccnu_id, password):
        handler.write("1")
        return True
    handler.write("0")


def changePasswordDo(handler):
    pass


class AccountHandler(BaseHandler):
    def get(self):
        self.write_error(403)
        return True

    def post(self):
        if not self.get_argument("action", None):
            self.write_error(403)
            return True
        {
            'login': loginDo,
            'register': registerDo,
            'logout': logoutDo,
            'restPassword': restPasswordDo,
        }.get(self.get_argument("action", None),
              lambda x: self.write(""))(self)
        return True