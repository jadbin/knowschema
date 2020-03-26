
import json

from guniflask.context import service

from knowschema.app import db
from knowschema.models import OperationRecord, EntityType, ClauseEntityTypeMapping, ClauseRecord

@service
class OperationRecordService:

    def property_type_record(self,
            operator,
            operation_type,
            entity_type_id,
            property_type_id,
            property_type_uri,
            new_prop,
            original_prop):

        data = {
            'operator': operator,
            'operation_type': operation_type,
            'entity_type_id': entity_type_id,
            'property_type_id': property_type_id,
            'property_type_uri': property_type_uri,
            'operated_field': None,
            'original_value': None,
            'new_value': None
        }

        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        data['entity_type_uri'] = entity_type.uri

        if operation_type == "UPDATE":
            for key, value in original_prop.items():
                if key in ['display_name', 'field_type', 'description']:
                    if value != new_prop[key]:
                        data['operated_field'] = key
                        data['original_value'] = value
                        data['new_value'] = new_prop[key]

                        new_record = OperationRecord.from_dict(data, ignore='id')
                        db.session.add(new_record)
            db.session.commit()
        elif operation_type == "CREATE":
            for key, value in new_prop.items():
                if key in ['display_name', 'field_type', 'description']:
                    data['operated_field'] = key
                    data['new_value'] = value

                    new_record = OperationRecord.from_dict(data, ignore='id')
                    db.session.add(new_record)
            db.session.commit()
        elif operation_type == "DELETE":
            data['property_type_id'] = None
            del original_prop['created_at']
            del original_prop['updated_at']
            store_value = json.dumps(original_prop)
            data['original_value'] = store_value

            new_record = OperationRecord.from_dict(data, ignore='id')
            db.session.add(new_record)
            db.session.commit()
        else:
            pass

    def update_property_type_record(self, operator, new_prop: dict, original_prop: object):
        self.property_type_record(operator, "UPDATE", original_prop.entity_type_id, original_prop.id,
                                                    new_prop['uri'], new_prop, original_prop.to_dict())

    def create_property_type_record(self, operator, new_prop):
        self.property_type_record(operator, "CREATE", new_prop.entity_type_id, new_prop.id,
                                                    new_prop.uri, new_prop.to_dict(), None)

    def delete_property_type_record(self, operator, property_type):
        self.property_type_record(operator, "DELETE", property_type.entity_type_id, property_type.id,
                                                    property_type.uri, None, property_type.to_dict())


    def entity_type_record(self,
            operator,
            operation_type,
            entity_type_id,
            new_prop,
            original_prop):

        trace_index = ['display_name', 'uri', 'description', 'father_id']
        data = {
            'operator': operator,
            'operation_type': operation_type,
            'entity_type_id': entity_type_id,
            'operated_field': None,
            'original_value': None,
            'new_value': None
        }

        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        data['entity_type_uri'] = entity_type.uri

        if operation_type == "UPDATE":
            for key, value in original_prop.items():
                if key in trace_index:
                    if value != new_prop.get(key):
                        data['operated_field'] = key
                        data['original_value'] = value
                        data['new_value'] = new_prop[key]

                        new_record = OperationRecord.from_dict(data, ignore='id')
                        db.session.add(new_record)
            db.session.commit()
        elif operation_type == "CREATE":
            for key, value in new_prop.items():
                if key in trace_index:
                    data['operated_field'] = key
                    data['new_value'] = value

                    new_record = OperationRecord.from_dict(data, ignore='id')
                    db.session.add(new_record)
            db.session.commit()
        elif operation_type == "DELETE":
            del original_prop['created_at']
            del original_prop['updated_at']
            store_value = json.dumps(original_prop)
            data['original_value'] = store_value

            new_record = OperationRecord.from_dict(data, ignore='id')
            db.session.add(new_record)
            db.session.commit()
        else:
            pass

    def create_entity_type_record(self, operator, new_entity_type):
        self.entity_type_record(operator, "CREATE", new_entity_type.id, new_entity_type.to_dict(), None)

    def update_entity_type_record(self, operator, new_entity: dict, original_entity: object):
        self.entity_type_record(operator, "UPDATE", original_entity.id, new_entity, original_entity.to_dict())

    def delete_entity_type_record(self, operator, entity_type):
        self.entity_type_record(operator, "DELETE", entity_type.id, None, entity_type.to_dict())

    def clause_mapping_record(self,
            operator,
            operation_type,
            clause_mapping_id,
            new_value,
            original_value):

        trace_index = [
            'clause_id',
            'clause_uri',
            'object_id',
            'object_uri',
            'object_name',
            'concept_id',
            'concept_uri',
            'concept_name',
            'condition',
            'description'
        ]

        data = {
            'operator': operator,
            'operation_type': operation_type,
            'clause_mapping_id': clause_mapping_id,
            'operated_field': None,
            'original_value': None,
            'new_value': None
        }

        if operation_type == "UPDATE":
            data['object_id'] = original_value['object_id']
            data['object_uri'] = original_value['object_uri']
            data['concept_id'] = original_value['concept_id']
            data['concept_uri'] = original_value['concept_uri']

            for key, value in original_value.items():
                if key in trace_index:
                    if value != new_value.get(key):
                        data['operated_field'] = key
                        data['original_value'] = value
                        data['new_value'] = new_value[key]

                        new_record = ClauseRecord.from_dict(data, ignore='id')
                        db.session.add(new_record)
            db.session.commit()
        elif operation_type == "CREATE":
            data['object_id'] = new_value['object_id']
            data['object_uri'] = new_value['object_uri']
            data['concept_id'] = new_value['concept_id']
            data['concept_uri'] = new_value['concept_uri']

            for key, value in new_value.items():
                if key in trace_index:
                    data['operated_field'] = key
                    data['new_value'] = value

                    new_record = ClauseRecord.from_dict(data, ignore='id')
                    db.session.add(new_record)
            db.session.commit()
        elif operation_type == "DELETE":
            del original_value['created_at']
            del original_value['updated_at']

            data['object_id'] = original_value['object_id']
            data['object_uri'] = original_value['object_uri']
            data['concept_id'] = original_value['concept_id']
            data['concept_uri'] = original_value['concept_uri']

            store_value = json.dumps(original_value)
            data['original_value'] = store_value

            new_record = ClauseRecord.from_dict(data, ignore='id')
            db.session.add(new_record)
            db.session.commit()
        else:
            pass

    def create_clause_mapping_record(self, operator, new_clause_mapping):
        self.clause_mapping_record(operator, "CREATE", new_clause_mapping.id, new_clause_mapping.to_dict(), None)

    def update_clause_mapping_record(self, operator, new_clause_mapping: dict, original_clause_mapping: object):
        self.clause_mapping_record(operator, "UPDATE", original_clause_mapping.id, new_clause_mapping, original_clause_mapping.to_dict())

    def delete_clause_mapping_record(self, operator, clause_mapping):
        self.clause_mapping_record(operator, "DELETE", clause_mapping.id, None, clause_mapping.to_dict())