from flask import request, abort, jsonify
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import Field, Clause, ClauseEntityTypeMapping, EntityType
from knowschema.services.operation_record import OperationRecordService
from knowschema.app import db


@blueprint('/api')
class ClauseController:
    def __init__(self, operation_record_service: OperationRecordService):
        self.operation_record_service = operation_record_service

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

    # @post_route('/clauses')
    # def create_clause(self):
    #     data = request.json
    #     clause = Clause.from_dict(data, ignore='id')
    #     db.session.add(clause)
    #     db.session.commit()
    #
    #     return jsonify(clause.to_dict())

    @get_route('/clause/all-mappings')
    def get_all_mappings(self):
        mappings = ClauseEntityTypeMapping.query.all()
        result = [i.to_dict() for i in mappings]
        return jsonify(result)

    @post_route("/clause/mapping")
    def create_clause_entity_type_mapping(self):
        data = request.json
        mapping = ClauseEntityTypeMapping.from_dict(data, ignore='id,created_at,updated_at')
        db.session.add(mapping)
        db.session.commit()

        operator = "admin"
        self.operation_record_service.create_clause_mapping_record(operator, mapping)

        return jsonify(mapping.to_dict())

    @put_route("/clause/mapping/<mapping_id>")
    def update_clause_entity_type_mapping(self, mapping_id):
        mapping = ClauseEntityTypeMapping.query.filter_by(id=mapping_id).first()
        if mapping is None:
            abort(404)


        data = request.json

        operator = "admin"
        self.operation_record_service.update_clause_mapping_record(operator, data, mapping)

        mapping.update_by_dict(data, ignore='id,create_at,updated_at')
        db.session.commit()

        return 'success'

    @delete_route('/clause/mapping/<mapping_id>')
    def delete_entity_type_clause_mapping(self, mapping_id):
        mapping_item = ClauseEntityTypeMapping.query.filter_by(id=mapping_id).first()
        if mapping_item is None:
            abort(404)

        operator = "admin"
        self.operation_record_service.delete_clause_mapping_record(operator, mapping_item)

        db.session.delete(mapping_item)
        db.session.commit()

        return 'success'

    @get_route('/clause/_checkout')
    def checkout(self):
        mappings = ClauseEntityTypeMapping.query.all()
        for mapping in mappings:
            clause = Clause.query.filter_by(id=mapping.clause_id).first()
            obj = EntityType.query.filter_by(id=mapping.object_id).first()
            concept = EntityType.query.filter_by(id=mapping.concept_id).first()

            data = mapping.to_dict()
            data['clause_uri'] = clause.uri
            data['object_uri'] = obj.uri
            data['concept_uri'] = concept.uri

            operator = "admin"
            self.operation_record_service.update_clause_mapping_record(operator, data, mapping)

            mapping.update_by_dict(data, ignore='id,create_at,updated_at')
        db.session.commit()

        return "success"