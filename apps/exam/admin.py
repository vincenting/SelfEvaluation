#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from core.web import BaseHandler, authenticated
from .models import *


class BankHandler(BaseHandler):
    current_nav = "bank"

    @authenticated
    def get(self):

        type2Model = {
            'chapter': ChapterModel,
            'section': SectionModel,
            'subject': SubjectModel,
            'choice': ChoiceModel
        }

        type2ChildModel = {
            'root': ChapterModel,
            'chapter': SectionModel,
            'section': SubjectModel,
            'subject': ChoiceModel
        }

        if not self.get_current_user()['is_teacher']:
            self.write_error(403)
            return True

        #首页没有parent参数时默认显示所有章
        if not self.get_argument("parent", None) and not self.get_argument("type", None):
            self.render("admin/root.html", chapters=self.db.query(ChapterModel).all())
            return True

        if not self.get_argument("parent", None) == "root" and not self.get_argument("action", None) == "update":
            parentModel = type2Model.get(self.get_argument("parent", None), ChapterModel)
            parent = self.db.query(parentModel).get(self.get_argument("parent_id", 0))
        else:
            parent = {}

        if parent is None:
            self.write_error(404)
            return True

        if not self.get_argument("action", None):
            self.render("admin/{0}.html".format(self.get_argument("parent", "")), parent=parent)
            return True

        if self.get_argument("action", None) not in ("create", "update"):
            self.write_error(404)
            return True

        if self.get_argument("action", None) == "create":
            self.render("admin/edit/{0}.html".format(self.get_argument("parent", "")),
                        item=None, parent=parent)
            return True

        item = self.db.query(type2ChildModel.get(self.get_argument("parent", None), ChapterModel)).get(
            self.get_argument("id", 0))
        self.render("admin/edit/{0}.html".format(self.get_argument("parent", "")),
                    item=item, parent=None)
        return True


    @authenticated
    def post(self):
        if not self.get_current_user()['is_teacher']:
            self.write_error(403)
            return True

        target2Model = {
            'chapters': (ChapterModel, ('chapter_name',)),
            'sections': (SectionModel, ('section_name', 'section_markdown', 'parent_chapter_id')),
            'subjects': (SubjectModel, ('subject_content', 'parent_section_id')),
            'choices': (ChoiceModel, ('choice_content', 'choice_correct', 'parent_subject_id'))
        }

        modelInfo = target2Model.get(self.get_argument("target", ()))
        if not modelInfo:
            self.write_error(404)

        model = modelInfo[0]
        if self.get_argument("action", None) == "create":
            kwargs = {}
            for item in modelInfo[1]:
                kwargs[item] = self.get_argument(item, None)
            new_item = model(**kwargs)
            self.db.add(new_item)
            self.db.commit()
            self.redirect("/admin/bank" if self.get_argument("parent", None) == "root" else
            "/admin/bank?parent={0}&parent_id={1}".format(self.get_argument("parent", ""),
                                                          self.get_argument("parent_id", "")))
            return True

        item_id = self.get_argument("id", None)
        if not item_id:
            self.write_error(404)
            return True
        this_item = self.db.query(model).get(item_id)
        if not this_item:
            self.write_error(404)
            return True

        if self.get_argument("action", None) == "delete":
            self.db.delete(this_item)
            self.db.commit()
            self.write("1")
            return True

        if self.get_argument("action", None) == "update":
            kwargs = {}
            for item in modelInfo[1]:
                setattr(this_item, item, self.get_argument(item, None))
                kwargs[item] = self.get_argument(item, None)
            self.db.commit()
            self.redirect("/admin/bank" if self.get_argument("parent", None) == "root" else
            "/admin/bank?parent={0}&parent_id={1}".format(self.get_argument("parent", ""),
                                                          self.get_argument("parent_id", "")))
            return True