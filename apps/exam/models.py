#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vincent Ting'

from core.models import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, UnicodeText
from sqlalchemy.orm import relationship, backref
from markdown import markdown


class ChapterModel(BaseModel):
    __tablename__ = 'chapters'
    chapter_id = Column(Integer, primary_key=True)
    chapter_name = Column(String(150), nullable=False)

    def __init__(self, chapter_name):
        self.chapter_name = chapter_name

    def __str__(self):
        return "<Chapter('{0}')>".format(self.chapter_name)


class SectionModel(BaseModel):
    __tablename__ = 'sections'
    section_id = Column(Integer, primary_key=True)
    section_name = Column(String(150), nullable=False)
    section_markdown = Column(Text(), nullable=False)
    section_introduction = Column(Text(), nullable=False)
    section_status = Column(Integer, nullable=False, default=0)
    parent_chapter_id = Column(Integer, ForeignKey('chapters.chapter_id'))
    chapter = relationship("ChapterModel", backref=backref('sections', order_by=section_id))

    def __init__(self, section_name, section_markdown, parent_chapter_id):
        self.section_name = section_name
        self.section_markdown = section_markdown
        self.section_introduction = markdown(section_markdown, output_format='html4')
        self.parent_chapter_id = parent_chapter_id

    def __str__(self):
        return "<Section('{0}')>".format(self.section_name)


class SubjectModel(BaseModel):
    __tablename__ = 'subjects'
    subject_id = Column(Integer, primary_key=True)
    subject_content = Column(Text(), nullable=False)
    parent_section_id = Column(Integer, ForeignKey('sections.section_id'))
    section = relationship("SectionModel", backref=backref('subjects', order_by=subject_id))
    img = Column(UnicodeText, nullable=True)

    def __init__(self, subject_content, parent_section_id):
        self.subject_content = subject_content
        self.parent_section_id = parent_section_id

    def __str__(self):
        return "<Subject('{0}')>".format(self.subject_content)


class ChoiceModel(BaseModel):
    __tablename__ = 'choices'
    choice_id = Column(Integer, primary_key=True)
    choice_content = Column(Text(), nullable=False)
    choice_correct = Column(Boolean, default=False, nullable=False)
    parent_subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    subject = relationship("SubjectModel", backref=backref('choices', order_by=choice_id))
    img = Column(UnicodeText, nullable=True)

    def __init__(self, choice_content, parent_subject_id, choice_correct):
        self.choice_content = choice_content
        self.parent_subject_id = parent_subject_id
        self.choice_correct = choice_correct

    def __str__(self):
        return "<Choice('{0}')>".format(self.choice_content)


class ChoiceRecordModel(BaseModel):
    __tablename__ = "choice_records"
    record_id = Column(Integer, primary_key=True)
    parent_user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("UserModel", backref=backref('choice_records', order_by=record_id))
    parent_section_id = Column(Integer, ForeignKey('sections.section_id'))
    section = relationship("SectionModel", backref=backref('choice_records', order_by=record_id))
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    subject = relationship("SubjectModel", backref=backref('choice_records', order_by=record_id))
    choice_result = Column(Boolean, nullable=True)

    def __init__(self, user_id, section_id, subject_id):
        self.parent_user_id = user_id
        self.parent_section_id = section_id
        self.subject_id = subject_id


class StudyRecordModel(BaseModel):
    __tablename__ = "study_records"
    record_id = Column(Integer, primary_key=True)
    parent_user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("UserModel", backref=backref('study_records', order_by=record_id))
    parent_section_id = Column(Integer, ForeignKey('sections.section_id'))
    section = relationship("SectionModel", backref=backref('study_records', order_by=record_id))
    study_result = Column(String(150), nullable=False)

    def __init__(self, user_id, section_id, result):
        self.parent_user_id = user_id
        self.parent_section_id = section_id
        self.study_result = result