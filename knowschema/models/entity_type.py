# coding=utf-8

from guniflask.orm import BaseModelMixin
from sqlalchemy import text as _text

from knowschema import db


class EntityType(BaseModelMixin, db.Model):
    __tablename__ = 'entity_type'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uri = db.Column(db.String(255), nullable=False, unique=True, index=True)
    display_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(255))
    father_id = db.Column(db.Integer, index=True, server_default=_text("'0'"))
    has_child = db.Column(db.SmallInteger, index=True, server_default=_text("'0'"))
    is_object = db.Column(db.Integer, server_default=_text("'0'"))
    created_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP"), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), default=db.func.now(), onupdate=db.func.now())
    algorithm_mappings = db.relationship('AlgorithmMapping', backref=db.backref('entity_type', lazy='joined'), cascade='all, delete-orphan', lazy='select')
    property_types = db.relationship('PropertyType', backref=db.backref('entity_type', lazy='joined'), cascade='all, delete-orphan', lazy='select')
