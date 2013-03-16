#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

import urllib
import hashlib
import tornado.web
from sqlalchemy.orm import scoped_session, sessionmaker
from .models import engine
from .session import Session
from apps.users.models import UserHandler


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        tornado.web.RequestHandler.initialize(self)
        self.db = scoped_session(sessionmaker(bind=engine))
        self.session = Session(self)
        self.userHandler = UserHandler(self)
        self.user = self.userHandler.auth()

    def get_current_user(self):
        return self.user

    def get_UA_md5(self):
        return hashlib.md5(self.request.headers['User-Agent']).hexdigest()

    def check_xsrf_cookie(self):
        token = (self.get_argument("_xsrf", None) or
                 self.request.headers.get("X-Xsrftoken") or
                 self.request.headers.get("X-Csrftoken"))
        if not token:
            self.send_error(403)
        if self.xsrf_token != token:
            self.send_error(403)

    def write_error(self, status_code, **kwargs):
        self.require_setting("static_path")
        if status_code in [404, 500, 503, 403]:
            self.write("Error occur - {0}".format(status_code))


class ErrorHandler(BaseHandler):
    def __init__(self, application, request, status_code):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.set_status(status_code)

    def prepare(self):
        self.send_error(self._status_code)


def authenticated(method):
    """
    验证用户权限的装饰器，如果设置了__roles__则需要验证权限，否则只需要登录
    :param method:
    :return: :raise:
    """
    @tornado.web.functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if tornado.web.urlparse.urlsplit(url).scheme:
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urllib.urlencode(dict(redirect=next_url))
                self.redirect(url)
                return
            raise tornado.web.HTTPError(403)
        try:
            need_roles = getattr(self,"__roles__")
            if type(need_roles) == type(""):
                need_roles = (need_roles,)
            if self.current_user.get('role',None) not in need_roles:
                raise tornado.web.HTTPError(403)
        except AttributeError:
            pass
        return method(self, *args, **kwargs)

    return wrapper


tornado.web.ErrorHandler = ErrorHandler