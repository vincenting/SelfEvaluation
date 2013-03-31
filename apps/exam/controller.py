#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from core.web import BaseHandler
from apps.exam.models import *
import random
import json


class IndexHandler(BaseHandler):
    def get(self):
        if not self.get_current_user():
            self.render("login.html")
            return True

        if self.get_argument("redirect", None):
            self.redirect(self.get_argument("redirect"))
            return True

        current_section = self.db.query(SectionModel).filter(SectionModel.section_status == 1).first()

        if self.get_argument("get", None) == "subjects":
            if not current_section or self.get_current_user()['is_teacher']:
                return True
            subjects = current_section.subjects
            if not subjects:
                return True
            study_result = self.db.query(StudyRecordModel).filter(
                StudyRecordModel.parent_section_id == current_section.section_id,
                StudyRecordModel.parent_user_id == self.get_current_user()['user_id']).first()
            if study_result:
                self.write("Finish")
                return True

            loaded_subjects = self.db.query(ChoiceRecordModel).filter(
                ChoiceRecordModel.parent_section_id == current_section.section_id,
                ChoiceRecordModel.parent_user_id == self.get_current_user()['user_id']).all()

            result = []
            if not len(loaded_subjects):
                subject_ids = [subject.subject_id for subject in subjects]
                random.shuffle(subject_ids)
                subject_ids = subject_ids[0:4]
                for subject_id in subject_ids:
                    print subject_id
                    new_record = ChoiceRecordModel(user_id=self.get_current_user()['user_id'],
                                                   section_id=current_section.section_id,
                                                   subject_id=subject_id)
                    self.db.add(new_record)
                self.db.commit()

            else:
                subject_ids = []
                for subject in loaded_subjects:
                    subject_ids.append(subject.subject_id)

            for subject_id in subject_ids:
                subject = self.db.query(SubjectModel).get(subject_id)
                choices = subject.choices
                result.append({
                    'id': subject.subject_id,
                    'subject': subject.subject_content,
                    'img': subject.img,
                    #TODO 严重bug，读取后影响修改数据库！
                    'multi_choice': self.db.query(ChoiceModel).filter(ChoiceModel.choice_correct == True,
                                                                      ChoiceModel.subject == subject).count() > 1,
                    'choices': [{'id': choice.choice_id, 'content': choice.choice_content,
                                 'img': choice.img} for choice in
                                choices]
                })
            self.write(json.dumps(result))
            return True

        self.render("index.html", current_section=current_section)
        return True

    def post(self):
        pass