#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from apps.exam.controller import IndexHandler
from apps.exam.admin import BankHandler
from apps.users.controller import AccountHandler,LogoutHandler
from apps.admin.controller import AdminHandler

routes = [
    (r"/", IndexHandler),
    (r"/account.do", AccountHandler),
    (r"/logout.do", LogoutHandler),
    (r"/admin", AdminHandler),
    (r"/admin/bank", BankHandler),
]