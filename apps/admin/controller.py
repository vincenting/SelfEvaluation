#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from core.web import BaseHandler, authenticated


class AdminHandler(BaseHandler):
    current_nav = "index"

    @authenticated
    def get(self):
        self.render("admin/index.html")