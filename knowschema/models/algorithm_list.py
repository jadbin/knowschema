# coding=utf-8

from knowschema import db


class AlgorithmList(db.Model):
    __tablename__ = 'algorithm_list'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    algorithm_name = db.Column(db.String(255))
