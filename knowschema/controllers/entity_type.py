# coding=utf-8

import logging

from flask import request, abort, jsonify
from sqlalchemy import or_, and_
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import EntityType, Clause, ClauseEntityTypeMapping
from knowschema.app import db
from knowschema.services.entity_type import EntityTypeService
from knowschema.services.operation_record import OperationRecordService

log = logging.getLogger(__name__)


@blueprint('/api')
class EntityTypeController:
    def __init__(self, entity_type_service: EntityTypeService, operation_record_service: OperationRecordService):
        self.entity_type_service = entity_type_service
        self.operation_record_service = operation_record_service

    @get_route('/entity-types/<entity_type_id>/children')
    def get_children(self, entity_type_id):
        entity_types = EntityType.query.filter_by(father_id=entity_type_id)
        result = []
        for entity_type in entity_types:
            d = entity_type.to_dict()
            result.append(d)
        return jsonify(result)

    @get_route('/entity-types/_all')
    def get_all_entity_types(self):
        entity_types = EntityType.query.all()
        result = [i.to_dict() for i in entity_types]
        return jsonify(result)

    @get_route('/entity-types/<entity_type_id>')
    def get_entity_type(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)

        d = entity_type.to_dict()
        property_types = []
        for p in entity_type.property_types:
            data = p.to_dict()
            clauses = []
            if p.is_entity:
                obj = EntityType.query.filter_by(uri=p.field_type).first()
                if obj is not None:
                    mappings = ClauseEntityTypeMapping.query.filter(
                        and_(ClauseEntityTypeMapping.object_id == entity_type.id,
                             ClauseEntityTypeMapping.concept_id == obj.id)).all()
                    for m in mappings:
                        clauses.append(m.clause.to_dict())
            data['clauses'] = clauses
            property_types.append(data)

        d['property_types'] = property_types
        d['parent_property_types'] = self.entity_type_service.get_inherited_properties(entity_type)
        return jsonify(d)

    @get_route('/entity-types/_uri')
    def get_entity_type_by_uri(self):
        entity_type_uri = request.args.get('uri')
        if entity_type_uri is None:
            abort(400)
        entity_type = EntityType.query.filter_by(uri=entity_type_uri).first()
        if entity_type is None:
            abort(404)
        return jsonify(entity_type.to_dict())

    @post_route('/entity-types')
    def create_entity_type(self):
        data = request.json
        entity_type = EntityType.from_dict(data, ignore='id')
        db.session.add(entity_type)
        db.session.commit()

        operator = "admin"
        self.operation_record_service.create_entity_type_record(operator, entity_type)

        return jsonify(entity_type.to_dict())

    @put_route('/entity-types/<entity_type_id>')
    def update_entity_type(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)

        data = request.json

        operator = "admin"
        self.operation_record_service.update_entity_type_record(operator, data, entity_type)

        entity_type.update_by_dict(data, ignore='id,create_at,updated_at')
        db.session.commit()

        return 'success'

    @delete_route('/entity-types/<entity_type_id>')
    def delete_entity_type(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)

        operator = "admin"
        self.operation_record_service.delete_entity_type_record(operator, entity_type)

        db.session.delete(entity_type)
        db.session.commit()

        return 'success'

    @get_route('/entity-types/clause/<entity_type_id>')
    def get_relative_clause(self, entity_type_id):
        mappings = ClauseEntityTypeMapping.query.filter(
            or_(ClauseEntityTypeMapping.concept_id == entity_type_id,
                ClauseEntityTypeMapping.object_id == entity_type_id)).all()
        items = []
        item_id = set()
        for mapping in mappings:
            item = Clause.query.filter_by(id=mapping.clause_id).first().to_dict()
            if item['id'] not in item_id:
                items.append(item)
                item_id.add(item['id'])
        return jsonify(items)

    @get_route('/entity-types/clause/uri/<entity_type_uri>')
    def get_entity_type_with_clause_by_uri(self, entity_type_uri):
        entity_type = EntityType.query.filter_by(uri=entity_type_uri).first()
        if entity_type is None:
            abort(404)

        mappings = ClauseEntityTypeMapping.query.filter_by(entity_type_id=entity_type.id).all()
        items = []
        for mapping in mappings:
            item = Clause.query.filter_by(id=mapping.clause_id).first().to_dict()
            items.append(item)
        return jsonify(items)
