# coding=utf-8

from flask import request, abort, jsonify
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import PropertyType, EntityType
from knowschema.app import db


@blueprint('/api')
class PropertyTypeController:
    def __init__(self):
        pass

    @get_route('entity-types/<entity_type_id>/property-types')
    def get_property_types(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)

        d = [p.to_dict() for p in entity_type.property_types]
        return jsonify(d)

    @post_route('/property-types')
    def create_property_type(self):
        data = request.json
        property_type = PropertyType.from_dict(data, ignore='id')
        db.session.add(property_type)

        entity_type_id = property_type.entity_type_id
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if len(entity_type.property_types) > 0:
            entity_type.has_child = True

        db.session.commit()
        return jsonify(property_type.to_dict())

    @put_route('/property-types/<property_type_id>')
    def update_property_type(self, property_type_id):
        property_type = PropertyType.query.filter_by(id=property_type_id).first()
        if property_type is None:
            abort(404)

        data = request.json
        property_type.update_by_dict(data, ignore='id,create_at,updated_at')
        db.session.commit()

        return 'success'

    @delete_route('/property-types/<property_type_id>')
    def delete_entity_type(self, property_type_id):
        property_type = PropertyType.query.filter_by(id=property_type_id).first()
        if property_type is None:
            abort(404)

        db.session.delete(property_type)

        entity_type_id = property_type.entity_type_id
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if len(entity_type.property_types) == 0:
            entity_type.has_child = False

        db.session.commit()

        return 'success'
