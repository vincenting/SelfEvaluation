#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from core.web import BaseHandler, authenticated
from apps.exam.models import SectionModel, StudyRecordModel
from apps.users.models import UserModel


class AdminHandler(BaseHandler):
    current_nav = "index"

    @authenticated
    def get(self):
        if not self.get_current_user()['is_teacher']:
            self.write_error(403)
            return True

        current_section = self.db.query(SectionModel).filter(SectionModel.section_status == 1).first()

        if self.get_argument("action", None) == "current_rest":
            if current_section:
                current_section.section_status = 2
                self.db.commit()
            self.redirect("/admin")
            return True

        all_sections = [] if current_section else self.db.query(SectionModel).filter(SectionModel.section_status == 0)
        finish_number, total_result, all_record = (None, None, None)
        if current_section:
            all_record = self.db.query(StudyRecordModel).filter(
                StudyRecordModel.parent_section_id == current_section.section_id).all()
            finish_number = "{0} / {1}".format(len(all_record), self.db.query(UserModel).filter(
                UserModel.is_teacher == False).count())
            total_result = [float(record.study_result) for record in all_record]
            total_result = '暂无' if not len(all_record) else sum(total_result) / len(all_record)
        self.render("admin/index.html", current_section=current_section, all_sections=all_sections,
                    finish_number=finish_number, total_result=total_result, all_record=all_record)
        return True

    @authenticated
    def post(self):
        if not self.get_current_user()['is_teacher']:
            self.write_error(403)
            return True

        if self.get_argument("action", None) == "set_current":
            current_section = self.db.query(SectionModel).filter(SectionModel.section_status == 1).first()
            if not current_section:
                new_section = self.get_argument("current_section", None)
                if new_section:
                    self.db.query(SectionModel).get(new_section).section_status = 1
                    self.db.commit()
        self.redirect("/admin")
        return True