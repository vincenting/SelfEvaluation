#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from apps.exam.controller import IndexHandler
from apps.users.controller import AccountHandler

routes = [
    (r"/", IndexHandler),
    (r"/account.do", AccountHandler),
]