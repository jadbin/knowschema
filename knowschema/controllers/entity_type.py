# coding=utf-8

import logging

from flask import request, abort, jsonify
from sqlalchemy import or_, and_
from sqlalchemy import exc
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import EntityType, Clause, ClauseEntityTypeMapping, PropertyType
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

        d['property_types'] = [i.to_dict() for i in entity_type.property_types]
        d['parent_property_types'] = self.entity_type_service.get_inherited_properties(entity_type)

        if entity_type.is_object == 1:
            mappings = ClauseEntityTypeMapping.query.filter_by(object_id=entity_type.id)
        else:
            mappings = ClauseEntityTypeMapping.query.filter_by(concept_id=entity_type.id)
        d['clauses'] = [i.to_dict() for i in mappings]

        return jsonify(d)

    @get_route('/entity-types/_uri')
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

    @get_route("/entity-types/like-query")
    def get_entity_type_by_like_query(self):
        query_str = request.args.get('query_str')
        entity_types = EntityType.query.filter(EntityType.display_name.like("%" + query_str + "%"))
        results = [i.to_dict() for i in entity_types]
        return jsonify(results)

    @post_route('/entity-types')
    def create_entity_type(self):
        data = request.json

        entity_type = EntityType.from_dict(data, ignore='id')

        try:
            db.session.add(entity_type)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI", 400
        except BaseException as e:
            db.session.rollback()
            log.error(e)
            abort(400)

        operator = "admin"
        self.operation_record_service.create_entity_type_record(operator, entity_type)

        if data['father_id'] != 0:
            parent = EntityType.query.filter_by(id=data['father_id']).first()
            if parent:
                parent_data = parent.to_dict()
                parent_data['has_child'] += 1
                parent.update_by_dict(parent_data, ignore='id,create_at,updated_at')
                db.session.commit()
            else:
                print(data['father_id'])

        return jsonify(entity_type.to_dict())

    @put_route('/entity-types/<entity_type_id>')
    def update_entity_type(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)

        data = request.json

        operator = "admin"
        self.operation_record_service.update_entity_type_record(operator, data, entity_type)

        if data['father_id'] != entity_type.father_id:
            if entity_type.father_id != 0:
                original_parent = EntityType.query.filter_by(id=entity_type.father_id).first()
                original_parent_data = original_parent.to_dict()
                original_parent_data['has_child'] -= 1
                original_parent.update_by_dict(original_parent_data, ignore='id,create_at,updated_at')

                if data['father_id'] != 0:
                    new_parent = EntityType.query.filter_by(id=data['father_id']).first()
                    new_parent_data = new_parent.to_dict()
                    new_parent_data['has_child'] += 1
                    new_parent.update_by_dict(new_parent_data, ignore='id,create_at,updated_at')

                db.session.commit()
            else:
                new_parent = EntityType.query.filter_by(id=data['father_id']).first()
                new_parent_data = new_parent.to_dict()
                new_parent_data['has_child'] += 1
                new_parent.update_by_dict(new_parent_data, ignore='id,create_at,updated_at')
                db.session.commit()

        if data['display_name'] != entity_type.display_name:
            property_types = PropertyType.query.filter_by(field_type=entity_type.display_name).all()
            for property_type in property_types:
                prop_data = property_type.to_dict()
                prop_data['field_type'] = data['display_name']

                self.operation_record_service.update_property_type_record(operator, prop_data, property_type)
                property_type.update_by_dict(prop_data, ignore='id,create_at,updated_at')
                db.session.commit()

        try:
            entity_type.update_by_dict(data, ignore='id,create_at,updated_at')
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI", 400
        except BaseException as e:
            db.session.rollback()
            log.error(e)
            abort(400)

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

        if entity_type.father_id != 0:
            parent = EntityType.query.filter_by(id=entity_type.father_id).first()
            if parent:
                parent_data = parent.to_dict()
                parent_data['has_child'] -= 1
                parent.update_by_dict(parent_data, ignore='id,create_at,updated_at')
                db.session.commit()
            else:
                print(entity_type.father_id)

        return 'success'

    @put_route("/entity-types/merge/<source_id>/<target_id>")
    def merge_entity_type(self, source_id, target_id):
        operator = "admin"

        source = EntityType.query.filter_by(id=source_id).first()
        target = EntityType.query.filter_by(id=target_id).first()
        target_data = target.to_dict()

        # merge children
        children = EntityType.query.filter_by(father_id=source_id).all()
        for child in children:
            child_data = child.to_dict()
            child_data['father_id'] = target_id

            target_data['has_child'] += 1

            self.operation_record_service.update_entity_type_record(operator, child_data, child)
            child.update_by_dict(child_data, ignore='id,create_at,updated_at')

        # merge property
        property_types = PropertyType.query.filter_by(entity_type_id=source_id).all()
        for property_type in property_types:
            prop_data = property_type.to_dict()
            prop_data['entity_type_id'] = target_id

            self.operation_record_service.update_property_type_record(operator, prop_data, property_type)
            property_type.update_by_dict(prop_data, ignore='id,create_at,updated_at')

        property_types = PropertyType.query.filter_by(field_type=source.uri).all()
        for property_type in property_types:
            prop_data = property_type.to_dict()
            prop_data['field_type'] = target.uri

            self.operation_record_service.update_property_type_record(operator, prop_data, property_type)
            property_type.update_by_dict(prop_data, ignore='id,create_at,updated_at')

        # merge mapping
        mappings = ClauseEntityTypeMapping.query.filter_by(object_id=source_id).all()
        for mapping in mappings:
            mapping_data = mapping.to_dict()
            mapping_data['object_id'] = target_id
            mapping_data['object_uri'] = target.uri

            self.operation_record_service.update_clause_mapping_record(operator, mapping_data, mapping)
            mapping.update_by_dict(mapping_data, ignore='id,create_at,updated_at')

        mappings = ClauseEntityTypeMapping.query.filter_by(concept_id=source_id).all()
        for mapping in mappings:
            mapping_data = mapping.to_dict()
            mapping_data['concept_id'] = target_id
            mapping_data['concept_uri'] = target.uri

            self.operation_record_service.update_clause_mapping_record(operator, mapping_data, mapping)
            mapping.update_by_dict(mapping_data, ignore='id,create_at,updated_at')

        # delete source
        if source.father_id != 0:
            parent = EntityType.query.filter_by(id=source.father_id).first()
            if parent:
                parent_data = parent.to_dict()
                parent_data['has_child'] -= 1
                parent.update_by_dict(parent_data, ignore='id,create_at,updated_at')
                db.session.commit()
            else:
                print(source.father_id)

        self.operation_record_service.delete_entity_type_record(operator, source)
        db.session.delete(source)

        self.operation_record_service.update_entity_type_record(operator, target_data, target)
        target.update_by_dict(target_data, ignore='id,create_at,updated_at')

        db.session.commit()

        return "success"

    @put_route("/entity-types/copy/<entity_type_id>")
    def copy_entity_type(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is None:
            abort(404)

        operator = "admin"

        # copy entity type
        copy_data = entity_type.to_dict()
        copy_data['uri'] += "(copy)"
        copy_data['display_name'] += "(copy)"
        copy_entity_type = EntityType.from_dict(copy_data, ignore='id,created_at,updated_at')

        try:
            db.session.add(copy_entity_type)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI", 400
        except BaseException as e:
            db.session.rollback()
            log.error(e)
            abort(400)

        self.operation_record_service.create_entity_type_record(operator, copy_entity_type)

        db.session.add(copy_entity_type)
        db.session.commit()

        if entity_type.father_id != 0:
            parent = EntityType.query.filter_by(id=entity_type.father_id).first()
            if parent:
                parent_data = parent.to_dict()
                parent_data['has_child'] += 1
                parent.update_by_dict(parent_data, ignore='id,create_at,updated_at')
                db.session.commit()
            else:
                print(entity_type.father_id)

        # copy property type
        property_types = PropertyType.query.filter_by(entity_type_id=entity_type_id).all()
        for property_type in property_types:
            copy_prop_data = property_type.to_dict()
            copy_prop_data['entity_type_id'] = copy_entity_type.id
            copy_property_type = PropertyType.from_dict(copy_prop_data, ignore='id,created_at,updated_at')

            db.session.add(copy_property_type)
            self.operation_record_service.create_property_type_record(operator, copy_property_type)
        db.session.commit()

        # copy mappings
        mappings = ClauseEntityTypeMapping.query.filter_by(object_id=entity_type_id).all()
        for mapping in mappings:
            copy_mapping_data = mapping.to_dict()
            copy_mapping_data['object_id'] = copy_entity_type.id
            copy_mapping_data['object_uri'] = copy_entity_type.uri

            copy_mapping = ClauseEntityTypeMapping.from_dict(copy_mapping_data, ignore='id,created_at,updated_at')
            db.session.add(copy_mapping)

            self.operation_record_service.create_clause_mapping_record(operator, copy_mapping)
        db.session.commit()

        mappings = ClauseEntityTypeMapping.query.filter_by(concept_id=entity_type_id).all()
        for mapping in mappings:
            copy_mapping_data = mapping.to_dict()
            copy_mapping_data['concept_id'] = copy_entity_type.id
            copy_mapping_data['concept_uri'] = copy_entity_type.uri

            copy_mapping = ClauseEntityTypeMapping.from_dict(copy_mapping_data, ignore='id,created_at,updated_at')
            db.session.add(copy_mapping)

            self.operation_record_service.create_clause_mapping_record(operator, copy_mapping)
        db.session.commit()

        return jsonify(copy_entity_type.to_dict())

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

    # @get_route('/entity-types/clause/uri/<entity_type_uri>')
    # def get_entity_type_with_clause_by_uri(self, entity_type_uri):
    #     entity_type = EntityType.query.filter_by(uri=entity_type_uri).first()
    #     if entity_type is None:
    #         abort(404)
    #
    #     mappings = ClauseEntityTypeMapping.query.filter_by(entity_type_id=entity_type.id).all()
    #     items = []
    #     for mapping in mappings:
    #         item = Clause.query.filter_by(id=mapping.clause_id).first().to_dict()
    #         items.append(item)
    #     return jsonify(items)

    @get_route('/entity-types/_checkout_child')
    def checkout_child(self):
        entity_types = EntityType.query.all()

        for entity_type in entity_types:
            data = entity_type.to_dict()
            data['has_child'] = 0

            entity_type.update_by_dict(data, ignore='id,create_at,updated_at')


        for entity_type in entity_types:
            if entity_type.father_id != 0:
                parent = EntityType.query.filter_by(id=entity_type.father_id).first()
                if parent:
                    data = parent.to_dict()
                    data['has_child'] += 1
                    parent.update_by_dict(data, ignore='id,create_at,updated_at')
                else:
                    log.warning(f"Entity Type : {entity_type.id} and its father : {entity_type.father_id}")

        db.session.commit()

        return "success"

    @get_route('/entity-types/_checkout_uri')
    def checkout_uri(self):
        entity_types = EntityType.query.all()

        for entity_type in entity_types:
            if entity_type.uri != entity_type.display_name:
                data = entity_type.to_dict()

                property_types = PropertyType.query.filter_by(field_type=data['display_name'])
                for property_type in property_types:
                    prop_data = property_type.to_dict()
                    prop_data['field_type'] = data['uri']

                    self.operation_record_service.update_property_type_record("admin", prop_data, property_type)
                    property_type.update_by_dict(prop_data, ignore='id,create_at,updated_at')

                if data['description'] == None:
                    data['description'] = "(备份：" + data['display_name'] + ")"
                else:
                    data['description'] += "(备份：" + data['display_name'] + ")"
                data['display_name'] = data['uri']

                self.operation_record_service.update_entity_type_record("admin", data, entity_type)
                entity_type.update_by_dict(data, ignore='id,create_at,updated_at')

        db.session.commit()

        return "success"

    @put_route("/entity-types/_checkout_is_object/<entity_type_id>")
    def checkout_is_object(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()

        children_queue = [entity_type.id]
        while True:
            current_entity_type_id = children_queue.pop()

            # update self
            current_entity_type = EntityType.query.filter_by(id=current_entity_type_id).first()
            data = current_entity_type.to_dict()
            data['is_object'] = 1
            current_entity_type.update_by_dict(data, ignore='id,create_at,updated_at')

            # get children
            children = EntityType.query.filter_by(father_id=current_entity_type_id).all()
            for child in children:
                children_queue.append(child.id)

            if len(children_queue) == 0:
                break

        db.session.commit()

        return "success"


    @put_route("/entity-types/_checkout_is_concept/<entity_type_id>")
    def checkout_is_concept(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()

        children_queue = [entity_type.id]
        while True:
            current_entity_type_id = children_queue.pop()

            # update self
            current_entity_type = EntityType.query.filter_by(id=current_entity_type_id).first()
            data = current_entity_type.to_dict()
            data['is_object'] = 0
            current_entity_type.update_by_dict(data, ignore='id,create_at,updated_at')

            # get children
            children = EntityType.query.filter_by(father_id=current_entity_type_id).all()
            for child in children:
                children_queue.append(child.id)

            if len(children_queue) == 0:
                break

        db.session.commit()

        return "success"