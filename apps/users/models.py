#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from datetime import datetime
from core.models import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, BigInteger
from sqlalchemy.orm import relationship, backref
import urllib2, urllib, re, cookielib, time


def CCNUAuth(su_id=None, su_psw=None, get_name=False):
    """
    根据学号和密码获取姓名、性别、宿舍号，失败返回false
    :param su_id:
    :param su_psw:
    :return:
    """
    if not (su_id and su_psw):
        return False

    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    opener.addheaders = [('Connection', 'Keep-Alive')]
    opener.addheaders = [('Cache-Control', 'no-cache')]
    url_login = "http://portal.ccnu.edu.cn/loginAction.do"
    body = (('userName', su_id), ('userPass', su_psw))
    if len(opener.open(url_login, urllib.urlencode(body)).read()) != 53:
        return False
    if not get_name:
        return True

    auth_result = opener.open('http://portal.ccnu.edu.cn/index_jg.jsp').read()
    name = re.compile("(.*?)&nbsp;").findall(auth_result)[1].decode('gb2312').encode('utf8').replace(' ', '')
    opener.open("http://portal.ccnu.edu.cn/roamingAction.do?appId=HSXG")
    info = opener.open("http://202.114.32.143/ccnuxg/xg/studentInfo.do?method=getStudentInfo").read().decode('GBK')
    sex = re.compile("<td height=\"21\">&nbsp;(.*?)</td>").findall(info)[0]
    room = re.compile("<td>&nbsp;(.*?)</td>").findall(info)[14]
    return {
        'username': name,
        'sex': sex,
        'room': room
    }


def getRandomKey(length):
    import random

    _keyRange = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
                 "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
                 "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G",
                 "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R",
                 "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2",
                 "3", "4", "5", "6", "7", "8", "9"]
    random.shuffle(_keyRange)
    return "".join(_keyRange[0:length])


def encryptPws(psw, salt):
    import hashlib

    return hashlib.md5(hashlib.md5(psw).hexdigest() + salt).hexdigest()


class UserModel(BaseModel):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False)
    email = Column(String(75), nullable=False, unique=True)
    create_date = Column(DateTime, nullable=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    psw_salt = Column(String(4), nullable=False)
    psw_result = Column(String(128), nullable=False)
    ccnu_id = Column(String(10), nullable=True)
    room = Column(String(75), nullable=True)
    sex = Column(String(4), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_teacher = Column(Boolean, default=False, nullable=False)

    def __init__(self, email, username):
        self.username = username
        self.email = email

    def setPassword(self, password):
        self.psw_salt = getRandomKey(4)
        self.psw_result = encryptPws(password, self.psw_salt)

    def __str__(self):
        return "<User({0},{1},{2})>".format(self.username, self.email, self.create_date)


class OnlineRecordModel(BaseModel):
    __tablename__ = "user_online_time"
    record_id = Column(Integer, primary_key=True)
    record_date = Column(Date, nullable=False, default=datetime.now().strftime('%Y-%m-%d'))
    total_time = Column(BigInteger, nullable=False, default=180)
    last_update = Column(BigInteger, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("UserModel", backref=backref('online_recodes', order_by=record_id))

    def __init__(self, user_id):
        self.user_id = user_id
        self.last_update = int(time.time())


USER_LOGIN_COOKIE = "current_id"


class UserHandler():
    def __init__(self, requestHandler):
        self.requestHandler = requestHandler
        self.db = self.requestHandler.db

    def updateOnlineRecord(self):
        user_id = self.requestHandler.get_current_user()['user_id']
        today = datetime.now().strftime('%Y-%m-%d')
        record = self.db.query(OnlineRecordModel).filter_by(user_id=user_id, record_date=today).first()
        if not record:
            record = OnlineRecordModel(user_id)
            self.db.add(record)
        else:
            now = int(time.time())
            record.total_time += min(180, now - record.last_update)
            record.last_update = now
        self.db.commit()

    def getUserInfoById(self, user_id):
        """
        根据ID获得用户的信息，如果有返回字典，不存在返回None
        :param user_id:
        :return:
        """
        current_user = self.db.query(UserModel).get(user_id)
        if not current_user:
            return None
        return {
            'user_id': current_user.user_id,
            'username': current_user.username,
            'email': current_user.email,
            'create_date': current_user.create_date,
            'is_teacher': 1 if current_user.is_teacher else 0

        }

    def auth(self):
        """
        验证当前cookie和session，成功返回用户资料字典，否则返回false
        :return:
        """
        current_user = self.requestHandler.get_secure_cookie(USER_LOGIN_COOKIE, None)
        if current_user:
            return self.getUserInfoById(current_user)
        return False

    def login(self, password, username=None, email=None):
        """
        根据用户名或者邮箱，配合密码进行登录验证
        :param password:
        :param username:
        :param email:
        :return:
        """
        if not password:
            return False
        current_user = None
        if email:
            current_user = self.db.query(UserModel).filter_by(email=email).first()
        elif username:
            current_user = self.db.query(UserModel).filter_by(username=username).first()
        if not current_user or not current_user.psw_result == encryptPws(password, current_user.psw_salt):
            return False
        self.requestHandler.set_secure_cookie(USER_LOGIN_COOKIE, str(current_user.user_id), expires_days=120)
        return True

    def createUser(self, email, password, username, ccnu_id, sex, room):
        """
        用户注册，成功后自动登录并返回True，失败返回False
        :param username:
        :param email:
        :param password:
        :param ccnu_id:
        """
        new_user = UserModel(username=username.lower(), email=email.lower())
        new_user.setPassword(password)
        new_user.sex = sex
        new_user.ccnu_id = ccnu_id
        new_user.room = room
        self.db.add(new_user)
        try:
            self.db.commit()
            return True
        except:
            return False

    def createTeacher(self, email, username, password):
        new_user = UserModel(username=username.lower(), email=email.lower())
        new_user.setPassword(password)
        new_user.is_teacher = True
        self.db.add(new_user)
        try:
            self.db.commit()
            return True
        except:
            return False

    def setPassword(self, ccnu_id, newPsw):
        current_user = self.db.query(UserModel).filter_by(ccnu_id=ccnu_id).first()
        current_user.setPassword(newPsw)
        try:
            self.db.commit()
            return True
        except:
            return False

    def checkEmail(self, email):
        """
        检测邮箱地址是否可用，可用返回False
        :param email:
        :return:
        """
        return self.db.query(UserModel).filter_by(email=email.lower()).count() == 0

    def logout(self):
        """
        退出登录状态
        :return:
        """
        self.requestHandler.clear_cookie(USER_LOGIN_COOKIE)
        return True