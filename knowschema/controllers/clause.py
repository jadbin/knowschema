import logging

from flask import request, abort, jsonify
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import Field, Clause, ClauseEntityTypeMapping
from knowschema.services.clause import ClauseService

log = logging.getLogger(__name__)

@blueprint('/api')
class ClauseController:
    def __init__(self, clause_service: ClauseService):
        self.clause_service = clause_service

    @get_route("/clause/all-fields")
    def get_all_field(self):
        fields = Field.query.all()
        result = [i.to_dict() for i in fields]
        return jsonify(result)

    @get_route("/clause/field/<field_id>")
    def get_field_all_clauses(self, field_id):
        items = Clause.query.filter_by(field_id=field_id)
        clauses = [i.to_dict() for i in items]
        for clause in clauses:
            mappings = ClauseEntityTypeMapping.query.filter_by(clause_id=clause.id).all()
            mappings = [i.to_dict() for i in mappings]
            clause['mappings'] = mappings

        return clauses

    @get_route("/clause/all-clauses")
    def get_all_clause(self):
        clauses = Clause.query.all()
        results = [i.to_dict() for i in clauses]
        return jsonify(results)

    @get_route('/clause/all-mappings')
    def get_all_mappings(self):
        mappings = ClauseEntityTypeMapping.query.all()
        result = [i.to_dict() for i in mappings]
        return jsonify(result)

    @post_route("/clause/mapping")
    def create_clause_entity_type_mapping(self):
        data = request.json
        result = self.clause_service.create_clause_mapping(data)
        return jsonify(result)

    @put_route("/clause/mapping/<mapping_id>")
    def update_clause_entity_type_mapping(self, mapping_id):
        mapping = ClauseEntityTypeMapping.query.filter_by(id=mapping_id).first()
        if mapping is None:
            abort(404)
        data = request.json
        self.clause_service.update_clause_mapping(data, mapping)
        return 'success'

    @delete_route('/clause/mapping/<mapping_id>')
    def delete_entity_type_clause_mapping(self, mapping_id):
        mapping = ClauseEntityTypeMapping.query.filter_by(id=mapping_id).first()
        if mapping is None:
            abort(404)

        self.clause_service.delete_clause_mapping(mapping)
        return 'success'

    @put_route('/clause/mapping/_checkout_uri')
    def checkout_uri(self):
        self.clause_service.checkout_uri()
        return "success"