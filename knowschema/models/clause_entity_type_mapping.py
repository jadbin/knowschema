# coding=utf-8

from knowschema import db


class ClauseEntityTypeMapping(db.Model):
    __tablename__ = 'clause_entity_type_mapping'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    concept_id = db.Column(db.Integer, nullable=False, index=True)
    object_id = db.Column(db.Integer, nullable=False, index=True)
    clause_id = db.Column(db.Integer, db.ForeignKey('clause.id'), nullable=False, index=True)
