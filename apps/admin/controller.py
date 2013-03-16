#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from core.web import BaseHandler, authenticated
from apps.exam.models import *

from utils import create_all
create_all()

class AdminHandler(BaseHandler):
    current_nav = "index"

    @authenticated
    def get(self):
        self.render("admin/index.html")


class BankHandler(BaseHandler):
    current_nav = "bank"

    @authenticated
    def get(self):
        if not self.get_current_user()['is_teacher']:
            self.write_error(403)
            return True
        if not self.get_argument("list", None):
            self.render("admin/chapters.html", allChapters=self.db.query(ChapterModel).all())
            return True
        if not self.get_argument("id"):
            self.write_error("404")
            return True
        if self.get_argument("list") == "chapter":
            chapter = self.db.query(ChapterModel).get(self.get_argument("id"))
            if not chapter:
                self.write_error(404)
                return True
            self.render("admin/sections.html", chapter=chapter)
            return True
        if self.get_argument("list") == "section":
            section = self.db.query(SectionModel).get(self.get_argument("id"))
            if not section:
                self.write_error(404)
                return True
            self.render("admin/subjects.html", section=section)
            return True
        if self.get_argument("list") == "subject":
            subject = self.db.query(SubjectModel).get(self.get_argument("id"))
            if not subject:
                self.write_error(404)
                return True
            self.render("admin/choices.html", subject=subject)
            return True

    @authenticated
    def post(self):
        target2Model = {
            'chapters': (ChapterModel,()),
            'sections': (SectionModel,()),
            'subjects': (SubjectModel,()),
            'choices': (ChoiceModel,())
        }
        model = target2Model.get(self.get_argument("target", ()))[0]
        if not model:
            self.write("0")
        if self.get_argument("action", None) == "create":

            return True
        item_id = self.get_argument("id", "")
        item = self.db.query(model).get(item_id)
        if not item:
            return True
        if self.get_argument("action", None) == "delete":
            self.db.delete(item)
            self.db.commit()
            self.write("1")
            return True
        if self.get_argument("action", None) == "update":

            return True