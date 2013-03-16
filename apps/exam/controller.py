#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from core.web import BaseHandler, authenticated


class IndexHandler(BaseHandler):

    def get(self):
        if not self.get_current_user():
            self.render("login.html")
            return True
        self.write(self.get_current_user()['username'])

    post = get