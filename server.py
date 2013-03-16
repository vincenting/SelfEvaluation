#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

import logging
from tornado import web
from tornado import httpserver
from tornado import ioloop
from tornado.options import  options, parse_command_line
from settings import  settings
from routes import routes
parse_command_line()

application = web.Application(routes, **settings)

if __name__ == "__main__":
    server = httpserver.HTTPServer(application)
    server.listen(options.port)
    logging.info("listening on :%s" % options.port)
    ioloop.IOLoop.instance().start()
