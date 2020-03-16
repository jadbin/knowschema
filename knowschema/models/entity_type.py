# coding=utf-8

from sqlalchemy import text as _text

from knowschema import db


class EntityType(db.Model):
    __tablename__ = 'entity_type'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uri = db.Column(db.String(255), nullable=False, index=True)
    display_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(255))
    father_id = db.Column(db.Integer, index=True, server_default=_text("'0'"))
    has_child = db.Column(db.SmallInteger, index=True, server_default=_text("'0'"))
    created_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP"), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), default=db.func.now(), onupdate=db.func.now())
    property_types = db.relationship('PropertyType', backref=db.backref('entity_type', lazy='joined'), cascade='all, delete-orphan', lazy='select')
    clause_entity_type_mappings = db.relationship('ClauseEntityTypeMapping', backref=db.backref('entity_type', lazy='joined'), cascade='all, delete-orphan', lazy='select')
