# coding=utf-8

from enum import Enum


class FiledType(Enum):
    INT = 'INT'
    FLOAT = 'FLOAT'
    STRING = 'STRING'
    BYTES = 'BYTES'
    DATE = 'DATE'
    TIME = 'TIME'
    DATETIME = 'DATETIME'
