# coding=utf-8

from guniflask.orm import BaseModelMixin
from sqlalchemy import text as _text

from knowschema import db


class Clause(BaseModelMixin, db.Model):
    __tablename__ = 'clause'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uri = db.Column(db.String(255), nullable=False, unique=True, index=True)
    content = db.Column(db.String(255))
    level = db.Column(db.Integer)
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'), index=True)
    time_limit = db.Column(db.String(255))
    insider = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP"), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), default=db.func.now(), onupdate=db.func.now())
    clause_entity_type_mappings = db.relationship('ClauseEntityTypeMapping', backref=db.backref('clause', lazy='joined'), cascade='all, delete-orphan', lazy='select')
