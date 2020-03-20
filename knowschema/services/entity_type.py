# coding=utf-8

from guniflask.context import service

from knowschema.models import EntityType


@service
class EntityTypeService:

    def get_inherited_properties(self, entity_type):
        parent_properties = []
        while entity_type.father_id > 0:
            father = EntityType.query.filter_by(id=entity_type.father_id).first()
            d = father.to_dict()
            d['property_types'] = [p.to_dict() for p in father.property_types]
            parent_properties.append(d)
            entity_type = father
        return parent_properties
