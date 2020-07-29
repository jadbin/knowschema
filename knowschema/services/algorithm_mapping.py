# coding=utf-8

import logging
import json
import csv

from guniflask.context import service
from sqlalchemy import exc

from knowschema.models import AlgorithmMapping, AlgorithmList, EntityType
from knowschema.app import db

log = logging.getLogger(__name__)

@service
class AlgorithmMappingService:

    def save_algorithm_mapping(self, alg_mappings):
        for entity_type_uri, algs in alg_mappings.items():
            entity_type = EntityType.query.filter_by(uri=entity_type_uri).first()
            if entity_type is not None:
                entity_type = entity_type.to_dict()
                new_mapping_data = {
                    "entity_type_uri": entity_type_uri,
                    "entity_type_id": entity_type['id'],
                    "algorithm": json.dumps(algs, ensure_ascii=False)
                }

                existed_mapping = AlgorithmMapping.query.filter_by(entity_type_id=entity_type['id']).first()
                if existed_mapping is not None:
                    self.update_algorithm_mapping(existed_mapping, new_mapping_data)
                else:
                    self.create_algorithm_mapping(new_mapping_data)

    def get_algorithm_by_entity_type_uri(self, entity_type_uri):
        alg_mapping = AlgorithmMapping.query.filter_by(entity_type_uri=entity_type_uri).first()
        if alg_mapping is None:
            log.warning(f"Not found alg mapping from entity type uri: {entity_type_uri}")
            return []
        else:
            algs = json.loads(alg_mapping.algorithm)
            return algs

    def get_child_and_parent_algorithm(self, entity_type_uri):
        child_algs = self.get_algorithm_by_entity_type_uri(entity_type_uri)

        child = EntityType.query.filter_by(uri=entity_type_uri).first()
        if child is not None and child.father_id != 0:
            parent = EntityType.query.filter_by(id=child.father_id).first()
            parent_algs = self.get_algorithm_by_entity_type_uri(parent.uri)
        else:
            parent_algs = []

        result = {
            "child_algs": child_algs,
            "parent_algs": parent_algs
        }
        return result

    def create_algorithm_mapping(self, new_mapping_data):
        new_mapping = AlgorithmMapping.from_dict(new_mapping_data, ignore="id,created_at,updated_at")

        try:
            db.session.add(new_mapping)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            log.warning(f"Create alg mapping {new_mapping_data} error : {e}")
        else:
            log.debug(f"Create alg mapping {new_mapping_data} successfully")

    def update_algorithm_mapping(self, existed_mapping, new_mapping_data):
        try:
            existed_mapping.update_by_dict(new_mapping_data, ignore="id,created_at,updated_at")
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            log.warning(f"Update alg mapping {new_mapping_data} error : {e}")
        else:
            log.debug(f"Update alg mapping {new_mapping_data} successfully")