# coding=utf-8

from guniflask.orm import BaseModelMixin
from sqlalchemy import text as _text

from knowschema import db


class Field(BaseModelMixin, db.Model):
    __tablename__ = 'field'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uri = db.Column(db.String(255), unique=True, index=True)
    count = db.Column(db.Integer)
    support = db.Column(db.String(255))
    description = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP"), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), default=db.func.now(), onupdate=db.func.now())
    books = db.relationship('Book', backref=db.backref('field', lazy='joined'), cascade='all, delete-orphan', lazy='select')
