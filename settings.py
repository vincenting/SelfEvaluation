#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from tornado.options import options, define
import os

define("port", default=8000, help="http port", type=int)
define("cookie_secret", default="3hyh4hy3hy4Itgtthhyhyoiqwe78HUHUI787")
define("login_url",default="/login.do")
define("db",default="mysql")

if 'VCAP_SERVICES' in os.environ:

    define("debug", default=False, help="debug mode", type=bool)
    import json

    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
    # XXX: avoid hardcoding here
    mysql_srv = vcap_services['mysql-5.1'][0]
    redis_srv = vcap_services['redis-2.2'][0]
    mysql_cred = mysql_srv['credentials']
    redis_cred = redis_srv['credentials']
    define("db_host", default=mysql_cred['hostname'], help="mysql server")
    define("db_name", default=mysql_cred['name'], help="database name")
    define("db_user", default=mysql_cred['user'], help="database user")
    define("db_pass", default=mysql_cred['password'], help="database password")
    define("redis_host", default=redis_cred['hostname'], help="mysql server")
    define("redis_port", default=redis_cred['port'], help="database password")
    define("redis_pass", default=redis_cred['password'], help="database password")

else:
    define("debug", default=True, help="debug mode", type=bool)
    define("db_host", default="localhost", help="mysql server")
    define("db_name", default="preview_exam", help="database name")
    define("db_user", default="root", help="database user")
    define("db_pass", default="930309", help="database password")
    define("redis_host", default="localhost", help="redis server")
    define("redis_port", default=6379, help="redis port")
    define("redis_pass", default=None, help="database password")


settings = dict(
    template_path="templates",
    static_path="static",
    xsrf_cookies=True,
    cookie_secret=options.cookie_secret,
    debug= options.debug,
    login_url= options.login_url,
)