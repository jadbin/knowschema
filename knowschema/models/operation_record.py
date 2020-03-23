# coding=utf-8

from sqlalchemy import text as _text

from knowschema import db


class OperationRecord(db.Model):
    __tablename__ = 'operation_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    operator = db.Column(db.String(255))
    operation_type = db.Column(db.String(255))
    entity_type_id = db.Column(db.Integer, index=True)
    entity_type_uri = db.Column(db.String(255))
    property_type_id = db.Column(db.Integer, index=True)
    property_type_uri = db.Column(db.String(255))
    operated_field = db.Column(db.String(255))
    original_value = db.Column(db.String(255))
    new_value = db.Column(db.String(255))
    operated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
