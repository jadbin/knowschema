# coding=utf-8

from sqlalchemy import text as _text

from knowschema import db


class FieldRecord(db.Model):
    __tablename__ = 'field_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    operator = db.Column(db.String(255))
    operation_type = db.Column(db.String(255))
    field_id = db.Column(db.Integer)
    book_id = db.Column(db.Integer)
    catalog_id = db.Column(db.Integer)
    clause_id = db.Column(db.Integer, index=True)
    operated_field = db.Column(db.String(255))
    original_value = db.Column(db.String(14800))
    new_value = db.Column(db.String(255))
    operated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
