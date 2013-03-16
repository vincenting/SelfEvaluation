#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from tornado import wsgi
from settings import  settings
from routes import routes
    
application = wsgi.WSGIApplication(routes, **settings)
