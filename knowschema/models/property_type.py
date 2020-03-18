# coding=utf-8

from sqlalchemy import text as _text

from knowschema import db


class PropertyType(db.Model):
    __tablename__ = 'property_type'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uri = db.Column(db.String(255), nullable=False, index=True)
    display_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(255))
    field_type = db.Column(db.String(255))
    is_entity = db.Column(db.SmallInteger, index=True, server_default=_text("'0'"))
    entity_type_id = db.Column(db.Integer, db.ForeignKey('entity_type.id'), nullable=False, index=True)
    created_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP"), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), default=db.func.now(), onupdate=db.func.now())
