# coding=utf-8

import logging

from guniflask.context import service

from knowschema.models import Clause, ClauseEntityTypeMapping, EntityType
from knowschema.services.operation_record import OperationRecordService
from knowschema.app import db

log = logging.getLogger(__name__)

@service
class ClauseService:

    def __init__(self, operation_record_service: OperationRecordService):
        self.operation_record_service = operation_record_service

    def update_clause(self, data, clause, operator="admin"):
        clause.update_by_dict(data, ignore="id")
        db.session.commit()

        return clause.to_dict()

    def create_clause_mapping(self, data, operator="admin"):
        mapping = ClauseEntityTypeMapping.from_dict(data, ignore='id,created_at,updated_at')

        db.session.add(mapping)
        db.session.commit()

        self.operation_record_service.create_clause_mapping_record(operator, mapping)

        return mapping.to_dict()

    def update_clause_mapping(self, data, mapping, operator="admin"):
        self.operation_record_service.update_clause_mapping_record(operator, data, mapping)

        mapping.update_by_dict(data, ignore='id,create_at,updated_at')
        db.session.commit()

        return mapping.to_dict()

    def delete_clause_mapping(self, mapping, operator="admin"):
        self.operation_record_service.delete_clause_mapping_record(operator, mapping)

        data = mapping.to_dict()

        db.session.delete(mapping)
        db.session.commit()

        return data

    def checkout_uri(self):
        operator = "admin"

        mappings = ClauseEntityTypeMapping.query.all()
        for mapping in mappings:
            clause = Clause.query.filter_by(id=mapping.clause_id).first()
            if clause is None:
                log.warning(f"Error clause id : {mapping.clause_id}")
                clause_uri = "(缺失)"
            else:
                clause_uri = clause.uri

            obj = EntityType.query.filter_by(id=mapping.object_id).first()
            if obj is None:
                log.warning(f"Error object id : {mapping.object_id}")
                object_uri = "(缺失)"
            else:
                object_uri = obj.uri

            concept = EntityType.query.filter_by(id=mapping.concept_id).first()
            if concept is None:
                log.warning(f"Error concept id : {mapping.concept_id}")
                concept_uri = "(缺失)"
            else:
                concept_uri = concept.uri

            data = mapping.to_dict()
            data['clause_uri'] = clause_uri
            data['object_uri'] = object_uri
            data['concept_uri'] = concept_uri

            self.operation_record_service.update_clause_mapping_record(operator, data, mapping)

            mapping.update_by_dict(data, ignore='id,create_at,updated_at')
        db.session.commit()