#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from core.web import BaseHandler, authenticated
from .models import *
import cStringIO
from json import loads, dumps


class BankHandler(BaseHandler):
    current_nav = "bank"

    @authenticated
    def get(self):
        if not self.get_current_user()['is_teacher']:
            self.write_error(403)
            return True

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

        img = None

        if self.get_argument("action", None) == "create":
            self.render("admin/edit/{0}.html".format(self.get_argument("parent", "")),
                        item=None, img=img, parent=parent)
            return True

        item = self.db.query(type2ChildModel.get(self.get_argument("parent", None), ChapterModel)).get(
            self.get_argument("id", 0))
        try:
            if item.img:
                img = loads(item.img)
        except AttributeError:
            pass
        self.render("admin/edit/{0}.html".format(self.get_argument("parent", "")),
                    item=item, img=img, parent=None)
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

        img = self.request.files and self.request.files.get("img", None)[0]
        if img and len(img['body']) < 40000:
            import Image

            buff = cStringIO.StringIO()
            buff.write(img['body'])
            img_content = img['body'].encode("base64").replace("\n", "")
            buff.seek(0)
            temp_img = Image.open(buff)
            img = dumps({
                'width': temp_img.size[0],
                'height': temp_img.size[1],
                'content': "data:image/{0};base64,{1}".format(temp_img.format.lower(), img_content)
            })

        model = modelInfo[0]
        if self.get_argument("action", None) == "create":
            kwargs = {}
            for item in modelInfo[1]:
                kwargs[item] = self.get_argument(item, None)
            new_item = model(**kwargs)
            if img:
                new_item.img = img
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
            if img:
                this_item.img = img
            self.db.commit()
            self.redirect("/admin/bank" if self.get_argument("parent", None) == "root" else
            "/admin/bank?parent={0}&parent_id={1}".format(
                self.get_argument("parent", ""),
                self.get_argument("parent_id", "")))
            return True