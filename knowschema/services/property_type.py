# coding=utf-8

from enum import Enum

from guniflask.context import service

from knowschema.app import db
from knowschema.models import PropertyType
from knowschema.services.operation_record import OperationRecordService


class FiledType(Enum):
    INT = 'INT'
    FLOAT = 'FLOAT'
    STRING = 'STRING'
    BYTES = 'BYTES'
    DATE = 'DATE'
    TIME = 'TIME'
    DATETIME = 'DATETIME'


@service
class PropertyTypeService:

    def __init__(self, operation_record_service: OperationRecordService):
        self.operation_record_service = operation_record_service

    def create_property_type(self, data, operator="admin"):
        property_type = PropertyType.from_dict(data, ignore='id,created_at,updated_at')

        db.session.add(property_type)
        db.session.commit()

        self.operation_record_service.create_property_type_record(operator, property_type)

        return property_type.to_dict()

    def update_property_type(self, data, property_type, operator="admin"):
        self.operation_record_service.update_property_type_record(operator, data, property_type)

        property_type.update_by_dict(data, ignore='id,create_at,updated_at')
        db.session.commit()

        return property_type.to_dict()

    def delete_property_type(self, property_type, operator="admin"):
        self.operation_record_service.delete_property_type_record(operator, property_type)

        data = property_type.to_dict()

        db.session.delete(property_type)
        db.session.commit()

        return data
