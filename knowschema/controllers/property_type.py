# coding=utf-8

from flask import request, abort, jsonify
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import PropertyType, EntityType
from knowschema.services.property_type import PropertyTypeService


@blueprint('/api')
class PropertyTypeController:
    def __init__(self, property_type_service: PropertyTypeService):
        self.property_type_service = property_type_service

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

        result = self.property_type_service.create_property_type(data)

        return jsonify(result)

    @put_route('/property-types/<property_type_id>')
    def update_property_type(self, property_type_id):
        property_type = PropertyType.query.filter_by(id=property_type_id).first()
        if property_type is None:
            abort(404)

        data = request.json

        self.property_type_service.update_property_type(data, property_type)

        return 'success'

    @delete_route('/property-types/<property_type_id>')
    def delete_entity_type(self, property_type_id):
        property_type = PropertyType.query.filter_by(id=property_type_id).first()
        if property_type is None:
            abort(404)

        self.property_type_service.delete_property_type(property_type)

        return 'success'

    @get_route("/property-types/_checkout_entity_type_uri")
    def checkout_entity_type_uri(self):
        property_types = PropertyType.query.all()
        for property_type in property_types:
            if property_type.is_entity == 1:
                entity_type = EntityType.query.filter_by(uri=property_type.field_type).first()
                if entity_type is None:
                    print(property_type.id, property_type.uri, property_type.field_type)

        return "success"
