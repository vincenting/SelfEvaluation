#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from apps.exam.controller import IndexHandler
from apps.users.controller import AccountHandler
from apps.admin.controller import BankHandler,AdminHandler

routes = [
    (r"/", IndexHandler),
    (r"/account.do", AccountHandler),
    (r"/admin", AdminHandler),
    (r"/admin/bank", BankHandler),
]