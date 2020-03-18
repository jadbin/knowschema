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

    @put_route('/property-types/_auto_create')
    def update_property_types_with_auto_create(self):
        data = request.json
        for d in data:
            if 'id' in d:
                property_type = PropertyType.query.filter_by(id=d['id']).first()
                property_type.update_by_dict(d, ignore='id,create_at,updated_at')
            else:
                property_type = PropertyType.from_dict(data)
                db.session.add(property_type)
        db.session.commit()

        return 'success'

    @delete_route('/property-types/<property_type_id>')
    def delete_entity_type(self, property_type_id):
        property_type = PropertyType.query.filter_by(id=property_type_id).first()
        if property_type is None:
            abort(404)

        db.session.delete(property_type)

        db.session.commit()

        return 'success'
