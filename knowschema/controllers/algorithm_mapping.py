import logging
import json

from flask import abort, jsonify, request

from guniflask.web import blueprint, post_route, get_route
from guniflask.scheduling import scheduled
from guniflask.config import settings

from knowschema.services.algorithm_mapping import AlgorithmMappingService, AlgorithmList
from knowschema.models import Clause, Catalog, Book, Field, EntityType, ClauseEntityTypeMapping
from knowschema.utils.unique_scheduled import unique_scheduled, unique_process

log = logging.getLogger(__name__)


@blueprint('/api')
class AlgorithmController:
    def __init__(self, algorithm_mapping_service: AlgorithmMappingService):
        self.algorithm_mapping_service = algorithm_mapping_service

    @get_route('/alg-list')
    def get_algorithm_list(self):
        algs = AlgorithmList.query.all()
        alg_list = []
        for alg in algs:
            alg_list.append(alg.algorithm_name)

        return jsonify(alg_list)

    @post_route('/alg-mapping')
    def save_new_algorithm_mapping(self):
        '''
        {
            "[entity_type_uri]": ["[alg_name]", "[alg_name]", ...],
            ...
        }
        '''
        data = request.json
        self.algorithm_mapping_service.save_algorithm_mapping(data)
        return "success"

    @get_route('/alg-mapping/<entity_type_id>')
    def get_entity_algorithm_by_id(self, entity_type_id):
        entity_type = EntityType.query.filter_by(id=entity_type_id).first()
        if entity_type is not None:
            result = self.algorithm_mapping_service.get_child_and_parent_algorithm(entity_type.uri)
            return jsonify(result)
        else:
            return "Cannot find such entity type", 500

    @get_route('/alg-mapping/uri')
    def get_entity_algorithm_by_uri(self):
        entity_type_uri = request.args.get("uri")
        result = self.algorithm_mapping_service.get_child_and_parent_algorithm(entity_type_uri)
        return jsonify(result)