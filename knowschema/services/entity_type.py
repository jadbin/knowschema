# coding=utf-8

import logging

from guniflask.context import service
from sqlalchemy import exc

from knowschema.app import db
from knowschema.models import EntityType, PropertyType, ClauseEntityTypeMapping, AlgorithmMapping
from knowschema.services.operation_record import OperationRecordService
from knowschema.services.property_type import PropertyTypeService
from knowschema.services.clause import ClauseService
from knowschema.services.algorithm_mapping import AlgorithmMappingService

log = logging.getLogger(__name__)

@service
class EntityTypeService:

    def __init__(self,
                 property_type_service: PropertyTypeService,
                 clause_service: ClauseService,
                 operation_record_service: OperationRecordService,
                 algorithm_mapping_service: AlgorithmMappingService):
        self.property_type_service = property_type_service
        self.clause_service = clause_service
        self.operation_record_service = operation_record_service
        self.algorithm_mapping_service = algorithm_mapping_service

    def create_entity_type(self, data, operator="admin"):
        entity_type = EntityType.from_dict(data, ignore='id,created_at,updated_at')
        try:
            db.session.add(entity_type)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI"
        else:
            self.operation_record_service.create_entity_type_record(operator, entity_type)

            if data['father_id'] != 0:
                parent = EntityType.query.filter_by(id=data['father_id']).first()
                if parent:
                    parent_data = parent.to_dict()
                    parent_data['has_child'] += 1
                    self.update_entity_type(parent_data, parent, operator)
                else:
                    print(data['father_id'])

            return entity_type.to_dict()

    def update_entity_type(self, data, entity_type, operator="admin"):
        if data['father_id'] != entity_type.father_id:
            if entity_type.father_id != 0:
                original_parent = EntityType.query.filter_by(id=entity_type.father_id).first()
                original_parent_data = original_parent.to_dict()
                original_parent_data['has_child'] -= 1
                self.update_entity_type(original_parent_data, original_parent, operator)

                if data['father_id'] != 0:
                    new_parent = EntityType.query.filter_by(id=data['father_id']).first()
                    new_parent_data = new_parent.to_dict()
                    new_parent_data['has_child'] += 1
                    self.update_entity_type(new_parent_data, new_parent, operator)
            else:
                new_parent = EntityType.query.filter_by(id=data['father_id']).first()
                new_parent_data = new_parent.to_dict()
                new_parent_data['has_child'] += 1
                self.update_entity_type(new_parent_data, new_parent, operator)

        if data['uri'] != entity_type.uri:
            # modify uri in property type
            property_types = PropertyType.query.filter_by(field_type=entity_type.uri).all()
            for property_type in property_types:
                prop_data = property_type.to_dict()
                prop_data['field_type'] = data['uri']
                self.property_type_service.update_property_type(prop_data, property_type, operator)

            # modify uri in clause mapping
            if entity_type.is_object == 1:
                mappings = ClauseEntityTypeMapping.query.filter_by(object_id=entity_type.id).all()
                for mapping in mappings:
                    mapping_data = mapping.to_dict()
                    mapping_data['object_uri'] = data['uri']
                    self.clause_service.update_mapping(mapping_data, mapping, operator)
            else:
                mappings = ClauseEntityTypeMapping.query.filter_by(concept_id=entity_type.id).all()
                for mapping in mappings:
                    mapping_data = mapping.to_dict()
                    mapping_data['concept_uri'] = data['uri']
                    self.clause_service.update_mapping(mapping_data, mapping, operator)

            # modify uri in alg mapping
            alg_mapping = AlgorithmMapping.query.filter_by(entity_type_id=entity_type.id).first()
            if alg_mapping is not None:
                alg_mapping_data = alg_mapping.to_dict()
                alg_mapping_data['entity_type_uri'] = data['uri']

                self.algorithm_mapping_service.update_algorithm_mapping(alg_mapping, alg_mapping_data)

            data['display_name'] = data['uri']

        original_data = entity_type.to_dict()
        try:
            entity_type.update_by_dict(data, ignore='id,create_at,updated_at')
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI"
        else:
            self.operation_record_service.update_entity_type_record(operator, data, original_data)
            return entity_type.to_dict()

    def delete_entity_type(self, entity_type, operator="admin"):
        # delete relative mapping
        if entity_type.is_object == 1:
            mappings = ClauseEntityTypeMapping.query.filter_by(object_id=entity_type.id).all()
        elif entity_type.is_object == 0:
            mappings = ClauseEntityTypeMapping.query.filter_by(concept_id=entity_type.id).all()

        for mapping in mappings:
            self.clause_service.delete_mapping(mapping, operator)

        # delete relative property
        property_types = PropertyType.query.filter_by(entity_type_id=entity_type.id).all()
        for property_type in property_types:
            self.property_type_service.delete_property_type(property_type)

        self.operation_record_service.delete_entity_type_record(operator, entity_type)

        data = entity_type.to_dict()
        db.session.delete(entity_type)
        db.session.commit()

        if entity_type.father_id != 0:
            parent = EntityType.query.filter_by(id=entity_type.father_id).first()
            if parent:
                parent_data = parent.to_dict()
                parent_data['has_child'] -= 1
                self.update_entity_type(parent_data, parent, operator)
            else:
                print(entity_type.father_id)

        return data

    def merge_entity_type(self, source, target, operator="admin"):
        source_id = source.id
        target_id = target.id
        target_data = target.to_dict()

        # merge children
        children = EntityType.query.filter_by(father_id=source_id).all()
        for child in children:
            child_data = child.to_dict()
            child_data['father_id'] = target_id
            self.update_entity_type(child_data, child, operator)
            target_data['has_child'] += 1

        # merge property
        property_types = PropertyType.query.filter_by(entity_type_id=source_id).all()
        for property_type in property_types:
            prop_data = property_type.to_dict()
            prop_data['entity_type_id'] = target_id
            self.property_type_service.update_property_type(prop_data, property_type, operator)

        property_types = PropertyType.query.filter_by(field_type=source.uri).all()
        for property_type in property_types:
            prop_data = property_type.to_dict()
            prop_data['field_type'] = target.uri
            self.property_type_service.update_property_type(prop_data, property_type, operator)

        # merge mapping
        mappings = ClauseEntityTypeMapping.query.filter_by(object_id=source_id).all()
        for mapping in mappings:
            mapping_data = mapping.to_dict()
            mapping_data['object_id'] = target_id
            mapping_data['object_uri'] = target.uri
            self.clause_service.update_mapping(mapping_data, mapping, operator)

        mappings = ClauseEntityTypeMapping.query.filter_by(concept_id=source_id).all()
        for mapping in mappings:
            mapping_data = mapping.to_dict()
            mapping_data['concept_id'] = target_id
            mapping_data['concept_uri'] = target.uri
            self.clause_service.update_mapping(mapping_data, mapping, operator)

        # delete source
        if source.father_id != 0:
            parent = EntityType.query.filter_by(id=source.father_id).first()
            if parent:
                parent_data = parent.to_dict()
                parent_data['has_child'] -= 1
                self.update_entity_type(parent_data, parent, operator)
            else:
                log.warning(f"Cannot find source father : {source.father_id}")

        self.delete_entity_type(source)

        self.update_entity_type(target_data, target)

    def copy_entity_type(self, copy_name, entity_type, operator="admin"):
        # copy entity type
        copy_data = entity_type.to_dict()
        if copy_name is None:
            copy_data['uri'] += "(copy)"
            copy_data['display_name'] += "(copy)"
        else:
            copy_data['uri'] = copy_name['uri']
            copy_data['display_name'] = copy_name['uri']
        copy_data['has_child'] = 0

        copy_entity_type = self.create_entity_type(copy_data, operator)
        if type(copy_entity_type) != dict:
            return "重复URI"

        if entity_type.father_id != 0:
            parent = EntityType.query.filter_by(id=entity_type.father_id).first()
            if parent:
                parent_data = parent.to_dict()
                parent_data['has_child'] += 1
                self.update_entity_type(parent_data, parent, operator)
            else:
                log.warning(f"Cannot find father : {entity_type.father_id}")

        # copy property type
        property_types = PropertyType.query.filter_by(entity_type_id=entity_type.id).all()
        for property_type in property_types:
            copy_prop_data = property_type.to_dict()
            copy_prop_data['entity_type_id'] = copy_entity_type['id']
            self.property_type_service.create_property_type(copy_prop_data, operator)

        # copy mappings
        mappings = ClauseEntityTypeMapping.query.filter_by(object_id=entity_type.id).all()
        for mapping in mappings:
            copy_mapping_data = mapping.to_dict()
            copy_mapping_data['object_id'] = copy_entity_type['id']
            copy_mapping_data['object_uri'] = copy_entity_type['uri']
            self.clause_service.create_mapping(copy_mapping_data, operator)

        mappings = ClauseEntityTypeMapping.query.filter_by(concept_id=entity_type.id).all()
        for mapping in mappings:
            copy_mapping_data = mapping.to_dict()
            copy_mapping_data['concept_id'] = copy_entity_type['id']
            copy_mapping_data['concept_uri'] = copy_entity_type['uri']
            self.clause_service.create_mapping(copy_mapping_data, operator)

        return copy_entity_type

    def set_meta_type(self, entity_type, is_object, operator="admin"):
        children_queue = [entity_type.id]
        while True:
            current_entity_type_id = children_queue.pop()

            # update self
            current_entity_type = EntityType.query.filter_by(id=current_entity_type_id).first()
            data = current_entity_type.to_dict()
            data['is_object'] = is_object
            self.update_entity_type(data, current_entity_type, operator)

            # get children
            children = EntityType.query.filter_by(father_id=current_entity_type_id).all()
            for child in children:
                children_queue.append(child.id)

            if len(children_queue) == 0:
                break
        return "success"

    def checkout_child(self, operator="admin"):
        entity_types = EntityType.query.all()

        for entity_type in entity_types:
            data = entity_type.to_dict()
            data['has_child'] = 0
            self.update_entity_type(data, entity_type, operator)

        for entity_type in entity_types:
            if entity_type.father_id != 0:
                parent = EntityType.query.filter_by(id=entity_type.father_id).first()
                if parent:
                    data = parent.to_dict()
                    data['has_child'] += 1
                    self.update_entity_type(data, parent, operator)
                else:
                    log.warning(f"Entity Type : {entity_type.id} and its father : {entity_type.father_id}")

    def checkout_uri(self, operator="admin"):
        entity_types = EntityType.query.all()

        for entity_type in entity_types:
            if entity_type.uri != entity_type.display_name:
                data = entity_type.to_dict()

                property_types = PropertyType.query.filter_by(field_type=data['display_name'])
                for property_type in property_types:
                    prop_data = property_type.to_dict()
                    prop_data['field_type'] = data['uri']
                    self.property_type_service.update_property_type(prop_data, property_type, operator)

                if entity_type.is_object == 1:
                    mappings = ClauseEntityTypeMapping.query.filter_by(object_id=entity_type.id).all()
                    for mapping in mappings:
                        mapping_data = mapping.to_dict()
                        mapping_data['object_uri'] = data['display_name']
                        self.clause_service.update_mapping(mapping_data, mapping, operator)
                else:
                    mappings = ClauseEntityTypeMapping.query.filter_by(concept_id=entity_type.id).all()
                    for mapping in mappings:
                        mapping_data = mapping.to_dict()
                        mapping_data['concept_uri'] = data['display_name']
                        self.clause_service.update_mapping(mapping_data, mapping, operator)

                if data['description'] == None:
                    data['description'] = "(备份：" + data['display_name'] + ")"
                else:
                    data['description'] += "(备份：" + data['display_name'] + ")"
                data['display_name'] = data['uri']
                self.update_entity_type(data, entity_type, operator)

    def restore_uri(self, operator="admin"):
        entity_types = EntityType.query.all()

        for entity_type in entity_types:
            if (entity_type.description is not None) and ("备份" in entity_type.description):
                data = entity_type.to_dict()

                original_uri = data['uri']
                new_uri = data['description'][4:-1]
                new_description = data['description'] + "(" + data['uri'] + ")"
                try:
                    data['display_name'] = new_uri
                    data['uri'] = new_uri
                    data['description'] = new_description
                    self.update_entity_type(data, entity_type, operator)
                except:
                    db.session.rollback()

                    new_uri = "#" + new_uri + "#" + original_uri
                    data['display_name'] = new_uri
                    data['uri'] = new_uri
                    data['description'] = new_description
                    self.update_entity_type(data, entity_type, operator)

                property_types = PropertyType.query.filter_by(field_type=original_uri)
                for property_type in property_types:
                    prop_data = property_type.to_dict()
                    prop_data['field_type'] = new_uri
                    self.property_type_service.update_property_type(prop_data, property_type, operator)

    def get_inherited_properties(self, entity_type):
        parent_properties = []
        while entity_type.father_id > 0:
            father = EntityType.query.filter_by(id=entity_type.father_id).first()
            d = father.to_dict()
            d['property_types'] = [p.to_dict() for p in father.property_types]
            parent_properties.append(d)
            entity_type = father
        return parent_properties
