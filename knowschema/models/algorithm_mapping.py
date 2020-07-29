# coding=utf-8

from sqlalchemy import text as _text

from knowschema import db


class AlgorithmMapping(db.Model):
    __tablename__ = 'algorithm_mapping'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entity_type_uri = db.Column(db.String(255))
    entity_type_id = db.Column(db.Integer, db.ForeignKey('entity_type.id'), index=True)
    algorithm = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP"), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), default=db.func.now(), onupdate=db.func.now())
