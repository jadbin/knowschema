import logging

from flask import request, abort, jsonify
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import Field, Book, Catalog, Clause, ClauseEntityTypeMapping
from knowschema.services.clause import ClauseService

log = logging.getLogger(__name__)

@blueprint('/api')
class ClauseController:
    def __init__(self, clause_service: ClauseService):
        self.clause_service = clause_service

    # @get_route("/clause/all-fields")
    @get_route("/clause/fields/all")
    def get_all_fields(self):
        fields = Field.query.all()
        result = [i.to_dict() for i in fields]
        return jsonify(result)

    # @get_route("/clause/field/<field_id>")
    @get_route("/clause/fields/<field_id>")
    def get_field(self, field_id: int):
        field = Field.query.filter_by(id=field_id).first()
        if field is None:
            abort(404)

        result = field.to_dict()
        result['books'] = [i.to_dict() for i in field.books]
        return jsonify(result)

    @get_route("/clause/fields/<field_id>/children")
    def get_field_children(self, field_id: int):
        books = Book.query.filter_by(field_id=field_id).all()
        results = [i.to_dict() for i in books]
        return jsonify(results)

    @put_route("/clause/fields/<field_id>")
    def update_field(self, field_id):
        field = Field.query.filter_by(id=field_id).first()
        if field is None:
            abort(404)
        data = request.json
        result = self.clause_service.update_field(data, field)
        return result

    @get_route("/clause/books/all")
    def get_all_books(self):
        books = Book.query.all()
        result = [i.to_dict() for i in books]
        return jsonify(result)

    @get_route("/clause/books/<book_id>")
    def get_book(self, book_id: int):
        print("****************************")
        book = Book.query.filter_by(id=book_id).first()
        if book is None:
            abort(404)

        result = book.to_dict()
        result['catalogs'] = [i.to_dict() for i in book.catalogs]
        return jsonify(result)

    @get_route("/clause/books/<book_id>/children")
    def get_book_children(self, book_id: int):
        catalogs = Catalog.query.filter_by(book_id=book_id).all()
        results = [i.to_dict() for i in catalogs]
        return jsonify(results)

    @put_route("/clause/books/<book_id>")
    def update_book(self, book_id):
        book = Book.query.filter_by(id=book_id).first()
        if book is None:
            abort(404)
        data = request.json
        result = self.clause_service.update_book(data, book)
        return result

    @get_route("/clause/catalogs/all")
    def get_all_catalogs(self):
        catalogs = Catalog.query.all()
        result = [i.to_dict() for i in catalogs]
        return jsonify(result)

    @get_route("/clause/catalogs/<catalog_id>")
    def get_catalog(self, catalog_id: int):
        catalog = Catalog.query.filter_by(id=catalog_id).first()
        if catalog is None:
            abort(404)

        result = catalog.to_dict()
        result['clauses'] = [i.to_dict() for i in catalog.clauses]
        return jsonify(result)

    @get_route("/clause/catalogs/<catalog_id>/children")
    def get_catalog_children(self, catalog_id: int):
        clauses = Clause.query.filter_by(catalog_id=catalog_id).all()
        results = [i.to_dict() for i in clauses]
        return jsonify(results)

    @put_route("/clause/catalogs/<catalog_id>")
    def update_catalog(self, catalog_id):
        catalog = Catalog.query.filter_by(id=catalog_id).first()
        if catalog is None:
            abort(404)
        data = request.json
        result = self.clause_service.update_catalog(data, catalog)
        return result

    # @get_route("/clause/all-clauses")
    @get_route("/clause/clauses/all")
    def get_all_clauses(self):
        clauses = Clause.query.all()
        results = [i.to_dict() for i in clauses]
        return jsonify(results)

    @get_route("/clause/clauses/<clause_id>")
    def get_clause(self, clause_id: int):
        clause = Clause.query.filter_by(id=clause_id).first()
        if clause is None:
            abort(404)
        result = clause.to_dict()
        result['mappings'] = [i.to_dict() for i in clause.clause_entity_type_mappings]
        return jsonify(result)

    # @put_route("/clause/<clause_id>")
    @put_route("/clause/clauses/<clause_id>")
    def update_clause(self, clause_id):
        clause = Clause.query.filter_by(id=clause_id).first()
        if clause is None:
            abort(404)
        data = request.json
        result = self.clause_service.update_clause(data, clause)
        return result

    # @get_route('/clause/all-mappings')
    @get_route('/clause/mappings/all')
    def get_all_mappings(self):
        mappings = ClauseEntityTypeMapping.query.all()
        result = [i.to_dict() for i in mappings]
        return jsonify(result)

    # @get_route("/clause/mapping/<clause_id>")
    @get_route("/clause/mappings/<clause_id>")
    def get_mapping(self, clause_id):
        mappings = ClauseEntityTypeMapping.query.filter_by(clause_id=clause_id).all()
        result = [i.to_dict() for i in mappings]
        return jsonify(result)

    # @post_route("/clause/mapping")
    @post_route("/clause/mappings")
    def create_mapping(self):
        data = request.json
        result = self.clause_service.create_mapping(data)
        return jsonify(result)

    # @put_route("/clause/mapping/<mapping_id>")
    @put_route("/clause/mappings/<mapping_id>")
    def update_mapping(self, mapping_id):
        mapping = ClauseEntityTypeMapping.query.filter_by(id=mapping_id).first()
        if mapping is None:
            abort(404)
        data = request.json
        self.clause_service.update_mapping(data, mapping)
        return 'success'

    # @delete_route('/clause/mapping/<mapping_id>')
    @delete_route('/clause/mappings/<mapping_id>')
    def delete_mapping(self, mapping_id):
        mapping = ClauseEntityTypeMapping.query.filter_by(id=mapping_id).first()
        if mapping is None:
            abort(404)

        self.clause_service.delete_mapping(mapping)
        return 'success'

    # @put_route('/clause/mapping/_checkout_uri')
    @put_route('/clause/mappings/_checkout_uri')
    def checkout_mapping_uri(self):
        self.clause_service.checkout_mapping_uri()
        return "success"