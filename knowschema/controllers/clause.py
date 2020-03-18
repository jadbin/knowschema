from flask import request, abort, jsonify
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import Field, Clause, ClauseEntityTypeMapping, EntityType
from knowschema.app import db


@blueprint('/api')
class ClauseController:
    def __init__(self):
        pass

    @get_route("/clause/all-fields")
    def get_all_field(self):
        fields = Field.query.all()
        result = [i.to_dict() for i in fields]
        return jsonify(result)

    @get_route("/clause/field/<field_id>")
    def get_field_item(self, field_id):
        items = Clause.query.filter_by(field_id=field_id)
        # result = [i.to_dict() for i in items]
        result = []
        for item in items:
            d = item.to_dict()
            d['entity_types'] = []
            entity_type_list = [p.to_dict() for p in item.clause_entity_type_mappings]
            for i in entity_type_list:
                entity_type_id = i['entity_type_id']
                entity_type = EntityType.query.filter_by(id=entity_type_id).first().to_dict()
                d['entity_types'].append(entity_type)
            result.append(d)
        return jsonify(result)

    @post_route("/clause/create-mapping")
    def create_entity_type_clause_mapping(self):
        data = request.json
        mapping = ClauseEntityTypeMapping.from_dict(data, ignore='id')
        db.session.add(mapping)
        db.session.commit()

        return jsonify(mapping.to_dict())

    @delete_route('/clause/delete-mapping/<entity_type_id>/<clause_id>')
    def delete_entity_type(self, entity_type_id, clause_id):
        mapping_item = ClauseEntityTypeMapping.query.filter_by(entity_type_id=entity_type_id,
                                                               clause_id=clause_id).first()
        if mapping_item is None:
            abort(404)

        db.session.delete(mapping_item)
        db.session.commit()

        return 'success'

    @post_route('/clauses')
    def create_clause(self):
        data = request.json
        clause = Clause.from_dict(data, ignore='id')
        db.session.add(clause)
        db.session.commit()

        return jsonify(clause.to_dict())
