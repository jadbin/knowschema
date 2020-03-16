# coding=utf-8

from knowschema import db


class Clause(db.Model):
    __tablename__ = 'clause'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uri = db.Column(db.String(255), nullable=False)
    content = db.Column(db.String(255))
    level = db.Column(db.Integer, nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False, index=True)
    clause_entity_type_mappings = db.relationship('ClauseEntityTypeMapping', backref=db.backref('clause', lazy='joined'), cascade='all, delete-orphan', lazy='select')
