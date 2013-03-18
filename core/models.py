#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from tornado.options import options

engine = create_engine("{0}://{1}:{2}@{3}/{4}?charset=utf8".format(
    options.db,
    options.db_user,
    options.db_pass,
    options.db_host,
    options.db_name
), echo=False)

BaseModel = declarative_base()