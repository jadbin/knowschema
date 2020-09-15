# coding=utf-8

from guniflask.orm import BaseModelMixin

from knowschema import db


class AlgorithmList(BaseModelMixin, db.Model):
    __tablename__ = 'algorithm_list'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    algorithm_name = db.Column(db.String(255))
