# coding=utf-8

from sqlalchemy import text as _text

from knowschema import db


class ClauseMappingRecord(db.Model):
    __tablename__ = 'clause_mapping_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    operator = db.Column(db.String(255))
    operation_type = db.Column(db.String(255))
    clause_mapping_id = db.Column(db.Integer, index=True)
    object_id = db.Column(db.Integer)
    object_uri = db.Column(db.String(255))
    concept_id = db.Column(db.Integer)
    concept_uri = db.Column(db.String(255))
    operated_field = db.Column(db.String(255))
    original_value = db.Column(db.String(14800))
    new_value = db.Column(db.String(255))
    operated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
