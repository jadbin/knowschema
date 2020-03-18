# coding=utf-8

from flask import request, abort, jsonify
from sqlalchemy import or_, and_
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import EntityType, Clause, ClauseEntityTypeMapping
from knowschema.app import db


@blueprint('/api')
class EntityTypeController:
    def __init__(self):
        pass

    @get_route('/entity-types/<entity_type_id>/children')
    def get_children(self, entity_type_id):
        entity_types = EntityType.query.filter_by(father_id=entity_type_id)
        result = []
        for entity_type in entity_types:
            d = entity_type.to_dict()
            property_types = []
            for p in entity_type.property_types:
                data = p.to_dict()
                clauses = []
                if p.is_entity:
                    obj = EntityType.query.filter_by(uri=p.field_type).first()
                    mappings = ClauseEntityTypeMapping.query.filter(
                        and_(ClauseEntityTypeMapping.object_id == entity_type.id,
                             ClauseEntityTypeMapping.concept_id == obj.id)).all()
                    for m in mappings:
                        clauses.append(m.clause.to_dict())
                data['clauses'] = clauses
                property_types.append(data)

            d['property_types'] = property_types
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
                mappings = ClauseEntityTypeMapping.query.filter(
                    and_(ClauseEntityTypeMapping.object_id == entity_type.id,
                         ClauseEntityTypeMapping.concept_id == obj.id)).all()
                for m in mappings:
                    clauses.append(m.clause.to_dict())
            data['clauses'] = clauses
            property_types.append(data)

        d['property_types'] = property_types
        return jsonify(d)

    @post_route('/entity-types')
    def create_entity_type(self):
        data = request.json
        entity_type = EntityType.from_dict(data, ignore='id')
        db.session.add(entity_type)
        db.session.commit()

        return jsonify(entity_type.to_dict())

    @put_route('/entity-types/<entity_type_id>')
    def update_entity_type(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)

        data = request.json
        entity_type.update_by_dict(data, ignore='id,create_at,updated_at')
        db.session.commit()

        return 'success'

    @delete_route('/entity-types/<entity_type_id>')
    def delete_entity_type(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)

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
    def get_entity_type_by_uri(self, entity_type_uri):
        entity_type = EntityType.query.filter_by(uri=entity_type_uri).first()
        if entity_type is None:
            abort(404)

        mappings = ClauseEntityTypeMapping.query.filter_by(entity_type_id=entity_type.id).all()
        items = []
        for mapping in mappings:
            item = Clause.query.filter_by(id=mapping.clause_id).first().to_dict()
            items.append(item)
        return jsonify(items)
