# coding=utf-8

from sqlalchemy import text as _text

from knowschema import db


class Catalog(db.Model):
    __tablename__ = 'catalog'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uri = db.Column(db.String(255), unique=True, index=True)
    number = db.Column(db.String(255))
    title = db.Column(db.String(255))
    public_org = db.Column(db.String(255))
    description = db.Column(db.String(255))
    text = db.Column(db.Text)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), index=True)
    created_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP"), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), default=db.func.now(), onupdate=db.func.now())
    clauses = db.relationship('Clause', backref=db.backref('catalog', lazy='joined'), cascade='all, delete-orphan', lazy='select')
