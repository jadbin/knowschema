# coding=utf-8

from guniflask.orm import BaseModelMixin
from sqlalchemy import text as _text

from knowschema import db


class Book(BaseModelMixin, db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uri = db.Column(db.String(255), unique=True, index=True)
    public_time = db.Column(db.String(255))
    public_org = db.Column(db.String(255))
    description = db.Column(db.String(255))
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), index=True)
    created_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP"), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), default=db.func.now(), onupdate=db.func.now())
    catalogs = db.relationship('Catalog', backref=db.backref('book', lazy='joined'), cascade='all, delete-orphan', lazy='select')
