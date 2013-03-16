#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from core.models import BaseModel, engine

metadata = BaseModel.metadata


def create_all():
    metadata.create_all(engine)