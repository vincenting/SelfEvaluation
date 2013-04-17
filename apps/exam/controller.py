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

        if self.get_current_user()['is_teacher']:
            self.redirect('/admin')
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
                subject_ids = subject_ids[0:8] if len(subject_ids) > 8 else subject_ids
                for subject_id in subject_ids:
                    print subject_id
                    new_record = ChoiceRecordModel(user_id=self.get_current_user()['user_id'],
                                                   section_id=current_section.section_id,
                                                   subject_id=subject_id)
                    self.db.add(new_record)
                self.db.commit()

            else:
                subject_ids = [subject.subject_id for subject in loaded_subjects]

            for subject_id in subject_ids:
                subject = self.db.query(SubjectModel).get(subject_id)
                choices = subject.choices
                result.append({
                    'id': subject.subject_id,
                    'subject': subject.subject_content,
                    'img': subject.img,
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
        if not self.get_current_user():
            return True
        current_section = self.db.query(SectionModel).filter(SectionModel.section_status == 1).first()
        if self.db.query(StudyRecordModel).filter(StudyRecordModel.parent_section_id == current_section.section_id,
                                                  StudyRecordModel.parent_user_id == self.get_current_user()[
                                                      'user_id']).first():
            return True
        spend_time = self.get_argument("spend_time", "Unknown")
        choice_data = json.loads(self.get_argument("choice_data", "{}"))
        loaded_subjects = self.db.query(ChoiceRecordModel).filter(
            ChoiceRecordModel.parent_section_id == current_section.section_id,
            ChoiceRecordModel.parent_user_id == self.get_current_user()[
                'user_id']).all()
        subject_ids = []
        subject_id_2_record = {}
        total_subjects = len(loaded_subjects)
        correct_subjects = 0
        for subject in loaded_subjects:
            subject_ids.append(subject.subject_id)
            subject_id_2_record[subject.subject_id] = subject

        for subject_id in subject_ids:
            subject = self.db.query(SubjectModel).get(subject_id)
            current_answer = choice_data.get(str(subject_id), [])
            current_correct = True
            for choice in subject.choices:
                if choice.choice_correct == True:
                    print str(choice.choice_id) in current_answer
                    if not str(choice.choice_id) in current_answer:
                        current_correct = False
                        break
                    else:
                        current_answer.remove(str(choice.choice_id))
            if current_correct and len(current_answer) == 0:
                subject_id_2_record[subject_id].choice_result = True
                correct_subjects += 1
        result = correct_subjects / float(total_subjects)
        record = StudyRecordModel(user_id=self.get_current_user()['user_id'],
                                  section_id=current_section.section_id,
                                  spend_time=spend_time,
                                  result=result)
        self.db.add(record)
        self.db.commit()
        if result == 1:
            result = "优，全部答对了！"
        elif result > .7:
            result = "良，多数题目都答对了"
        elif result > .5:
            result = "及格，答对了一半"
        else:
            result = "有待提高，很多题目都答错了"
        self.write(result)
        return True