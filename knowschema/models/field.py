# coding=utf-8

from knowschema import db


class Field(db.Model):
    __tablename__ = 'field'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uri = db.Column(db.String(255))
    title = db.Column(db.String(255), nullable=False)
    clauses = db.relationship('Clause', backref=db.backref('field', lazy='joined'), cascade='all, delete-orphan', lazy='select')
