# coding=utf-8

from sqlalchemy import text as _text

from knowschema import db


class ClauseEntityTypeMapping(db.Model):
    __tablename__ = 'clause_entity_type_mapping'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clause_id = db.Column(db.Integer, db.ForeignKey('clause.id'), nullable=False, index=True)
    clause_uri = db.Column(db.String(255))
    object_id = db.Column(db.Integer, index=True)
    object_uri = db.Column(db.String(255))
    object_name = db.Column(db.String(255))
    concept_id = db.Column(db.Integer, index=True)
    concept_uri = db.Column(db.String(255))
    concept_name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    condition = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP"), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), default=db.func.now(), onupdate=db.func.now())
