# coding=utf-8

import logging

from flask import request, abort, jsonify
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import EntityType, ClauseEntityTypeMapping
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

    @get_route('/entity-types/<entity_type_id>')
    def get_entity_type(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)

        d = entity_type.to_dict()
        d['property_types'] = [i.to_dict() for i in entity_type.property_types]
        d['parent_property_types'] = self.entity_type_service.get_inherited_properties(entity_type)

        if entity_type.is_object == 1:
            mappings = ClauseEntityTypeMapping.query.filter_by(object_id=entity_type.id)
        else:
            mappings = ClauseEntityTypeMapping.query.filter_by(concept_id=entity_type.id)
        d['clauses'] = [i.to_dict() for i in mappings]

        return jsonify(d)

    # @get_route('/entity-types/_uri')
    @get_route('/entity-types/uri')
    def get_entity_type_by_uri(self):
        entity_type_uri = request.args.get('uri')
        if entity_type_uri is None:
            abort(400)
        entity_type = EntityType.query.filter_by(uri=entity_type_uri).first()
        if entity_type is None:
            abort(404)

        d = entity_type.to_dict()
        d['property_types'] = [i.to_dict() for i in entity_type.property_types]
        d['parent_property_types'] = self.entity_type_service.get_inherited_properties(entity_type)

        if entity_type.is_object == 1:
            mappings = ClauseEntityTypeMapping.query.filter_by(object_id=entity_type.id)
        else:
            mappings = ClauseEntityTypeMapping.query.filter_by(concept_id=entity_type.id)
        d['clauses'] = [i.to_dict() for i in mappings]

        return jsonify(entity_type.to_dict())

    # @get_route('/entity-types/_all')
    @get_route('/entity-types/all')
    def get_all_entity_types(self):
        entity_types = EntityType.query.all()
        result = [i.to_dict() for i in entity_types]
        return jsonify(result)

    @post_route('/entity-types')
    def create_entity_type(self):
        data = request.json
        result = self.entity_type_service.create_entity_type(data)
        if type(result) != dict:
            return result, 400
        else:
            return jsonify(result)

    @put_route('/entity-types/<entity_type_id>')
    def update_entity_type(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)
        data = request.json
        result = self.entity_type_service.update_entity_type(data, entity_type)
        if type(result) != dict:
            return result, 400
        else:
            return 'success'

    @delete_route('/entity-types/<entity_type_id>')
    def delete_entity_type(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)
        self.entity_type_service.delete_entity_type(entity_type)
        return 'success'

    @put_route("/entity-types/merge/<source_id>/<target_id>")
    def merge_entity_type(self, source_id, target_id):
        source = EntityType.query.filter_by(id=source_id).first()
        target = EntityType.query.filter_by(id=target_id).first()

        if source is None:
            return "无对应源实体类型", 400
        if target is None:
            return "无对应目标实体类型", 400

        self.entity_type_service.merge_entity_type(source, target)

        return "success"

    @put_route("/entity-types/copy/<entity_type_id>")
    def copy_entity_type(self, entity_type_id):
        copy_name = request.json
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)

        result = self.entity_type_service.copy_entity_type(copy_name, entity_type)
        if type(result) != dict:
            return result, 400
        else:
            return jsonify(result)

    # @put_route("/entity-types/_checkout_is_object/<entity_type_id>")
    @put_route("/entity-types/set-object/<entity_type_id>")
    def set_object(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        self.entity_type_service.set_meta_type(entity_type, is_object=1)
        return "success"

    # @put_route("/entity-types/_checkout_is_concept/<entity_type_id>")
    @put_route("/entity-types/set-concept/<entity_type_id>")
    def set_concept(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        self.entity_type_service.set_meta_type(entity_type, is_object=0)
        return "success"

    @put_route('/entity-types/_checkout_child')
    def checkout_child(self):
        self.entity_type_service.checkout_child()
        return "success"

    @put_route('/entity-types/_checkout_uri')
    def checkout_uri(self):
        self.entity_type_service.checkout_uri()
        return "success"

    @put_route('/entity-types/_restore_uri')
    def restore_uri(self):
        self.entity_type_service.restore_uri()
        return "success"

    @get_route("/entity-types/_find_unmatch")
    def find_unmatch(self):
        entity_types = EntityType.query.all()
        for entity_type in entity_types:
            if entity_type.uri != entity_type.display_name:
                print(entity_type.id, entity_type.uri, entity_type.display_name)
        return "success"