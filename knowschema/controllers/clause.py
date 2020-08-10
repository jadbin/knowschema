import logging
import os

from flask import request, abort, jsonify
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route
from guniflask.config import settings

from knowschema.models import Field, Book, Catalog, Clause, ClauseEntityTypeMapping
from knowschema.services.clause import ClauseService
from knowschema.services.algorithm_mapping import AlgorithmMappingService

log = logging.getLogger(__name__)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['csv'])
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@blueprint('/api')
class ClauseController:
    def __init__(self,
                 clause_service: ClauseService,
                 algorithm_mapping_service: AlgorithmMappingService):
        self.clause_service = clause_service
        self.algorithm_mapping_service = algorithm_mapping_service

    @get_route('/clause/all')
    def get_all(self):
        results = []

        # add field
        fields = Field.query.all()
        for field in fields:
            field_data = field.to_dict()
            field_data['id'] = "field_" + str(field_data['id'])
            field_data['books'] = []

            # add book
            books = field.books
            for book in books:
                book_data = book.to_dict()
                book_data['id'] = "book_" + str(book_data['id'])
                book_data['catalogs'] = []

                # add catalog
                catalogs = book.catalogs
                for catalog in catalogs:
                    catalog_data = catalog.to_dict()
                    catalog_data['id'] = "catalog_" + str(catalog_data['id'])
                    catalog_data['clauses'] = []

                    # add clause
                    clauses = catalog.clauses
                    for clause in clauses:
                        clause_data = clause.to_dict()
                        clause_data['id'] = "clause_" + str(clause_data['id'])
                        catalog_data['clauses'].append(clause_data)

                    book_data['catalogs'].append(catalog_data)

                field_data['books'].append(book_data)

            results.append(field_data)

        return jsonify(results)

    @get_route("/clause/fields/all")
    def get_all_fields(self):
        fields = Field.query.all()
        result = [i.to_dict() for i in fields]
        return jsonify(result)

    @get_route("/clause/fields/<field_id>")
    def get_field(self, field_id: int):
        field = Field.query.filter_by(id=field_id).first()
        if field is None:
            abort(404)

        result = field.to_dict()
        result['books'] = [i.to_dict() for i in field.books]
        return jsonify(result)

    @get_route("/clause/fields/uri")
    def get_field_by_uri(self):
        field_uri = request.args.get('uri')
        if field_uri is None:
            abort(400)

        field = Field.query.filter_by(uri=field_uri).first()
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

    @post_route("/clause/fields")
    def create_field(self):
        data = request.json
        result = self.clause_service.create_field(data)
        if type(result) != dict:
            return result, 400
        else:
            return jsonify(result)

    @put_route("/clause/fields/<field_id>")
    def update_field(self, field_id):
        field = Field.query.filter_by(id=field_id).first()
        if field is None:
            abort(404)
        data = request.json
        result = self.clause_service.update_field(data, field)
        return result

    @delete_route('/clause/fields/<field_id>')
    def delete_field(self, field_id):
        field = Field.query.filter_by(id=field_id).first()
        if field is None:
            abort(404)
        self.clause_service.delete_field(field)
        return 'success'

    @get_route("/clause/books/all")
    def get_all_books(self):
        books = Book.query.all()
        result = [i.to_dict() for i in books]
        return jsonify(result)

    @get_route("/clause/books/<book_id>")
    def get_book(self, book_id: int):
        book = Book.query.filter_by(id=book_id).first()
        if book is None:
            abort(404)

        result = book.to_dict()
        result['catalogs'] = [i.to_dict() for i in book.catalogs]
        return jsonify(result)

    @get_route("/clause/books/uri")
    def get_book_by_uri(self):
        book_uri = request.args.get('uri')
        if book_uri is None:
            abort(400)

        book = Book.query.filter_by(uri=book_uri).first()
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

    @post_route("/clause/books")
    def create_book(self):
        data = request.json
        result = self.clause_service.create_book(data)
        if type(result) != dict:
            return result, 400
        else:
            return jsonify(result)

    @put_route("/clause/books/<book_id>")
    def update_book(self, book_id):
        book = Book.query.filter_by(id=book_id).first()
        if book is None:
            abort(404)
        data = request.json
        result = self.clause_service.update_book(data, book)
        return result

    @delete_route('/clause/books/<book_id>')
    def delete_book(self, book_id):
        book = Book.query.filter_by(id=book_id).first()
        if book is None:
            abort(404)
        self.clause_service.delete_book(book)
        return 'success'

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

    @get_route("/clause/catalogs/uri")
    def get_catalog_by_uri(self):
        catalog_uri = request.args.get('uri')
        if catalog_uri is None:
            abort(400)

        catalog = Catalog.query.filter_by(uri=catalog_uri).first()
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

    @get_route("/clause/catalogs/by-book-uri")
    def get_catalog_by_book_uri(self):
        book_uri = request.args.get("uri")
        book = Book.query.filter_by(uri=book_uri).first()
        if book is not None:
            catalogs = Catalog.query.filter_by(book_id=book.id).all()
            result = [i.to_dict() for i in catalogs]

            return jsonify(result)
        else:
            return "Cannot find such book.", 400

    @post_route("/clause/catalogs")
    def create_catalog(self):
        data = request.json
        result = self.clause_service.create_catalog(data)
        if type(result) != dict:
            return result, 400
        else:
            return jsonify(result)

    @put_route("/clause/catalogs/<catalog_id>")
    def update_catalog(self, catalog_id):
        catalog = Catalog.query.filter_by(id=catalog_id).first()
        if catalog is None:
            abort(404)
        data = request.json
        result = self.clause_service.update_catalog(data, catalog)
        return result

    @delete_route('/clause/catalogs/<catalog_id>')
    def delete_catalog(self, catalog_id):
        catalog = Catalog.query.filter_by(id=catalog_id).first()
        if catalog is None:
            abort(404)
        self.clause_service.delete_catalog(catalog)
        return 'success'

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

    @get_route("/clause/clauses/by-catalog-uri")
    def get_clause_by_catalog_uri(self):
        catalog_uri = request.args.get("uri")
        catalog = Catalog.query.filter_by(uri=catalog_uri).first()
        if catalog is not None:
            clauses = Clause.query.filter_by(catalog_id=catalog.id).all()
            result = [i.to_dict() for i in clauses]

            return jsonify(result)
        else:
            return "Cannot find such catalog.", 400

    @get_route("/clause/clauses/uri")
    def get_clause_by_uri(self):
        clause_uri = request.args.get('uri')
        if clause_uri is None:
            abort(400)

        clause = Clause.query.filter_by(uri=clause_uri).first()
        if clause is None:
            abort(404)
        result = clause.to_dict()
        # result['mappings'] = [i.to_dict() for i in clause.clause_entity_type_mappings]
        result['mappings'] = []
        for mapping in clause.clause_entity_type_mappings:
            mapping_data = mapping.to_dict()

            object_uri = mapping_data['object_uri']
            concept_uri = mapping_data['concept_uri']

            object_algs = self.algorithm_mapping_service.get_child_and_parent_algorithm(object_uri)
            concept_algs = self.algorithm_mapping_service.get_child_and_parent_algorithm(concept_uri)

            mapping_data['object_algs'] = object_algs
            mapping_data['concept_algs'] = concept_algs

            result['mappings'].append(mapping_data)

        return jsonify(result)

    @post_route("/clause/clauses")
    def create_clause(self):
        data = request.json
        result = self.clause_service.create_clause(data)
        if type(result) != dict:
            return result, 400
        else:
            return jsonify(result)

    @put_route("/clause/clauses/<clause_id>")
    def update_clause(self, clause_id):
        clause = Clause.query.filter_by(id=clause_id).first()
        if clause is None:
            abort(404)
        data = request.json
        result = self.clause_service.update_clause(data, clause)
        return result

    @delete_route('/clause/clauses/<clause_id>')
    def delete_clause(self, clause_id):
        clause = Clause.query.filter_by(id=clause_id).first()
        if clause is None:
            abort(404)
        self.clause_service.delete_clause(clause)
        return 'success'

    @get_route('/clause/mappings/all')
    def get_all_mappings(self):
        mappings = ClauseEntityTypeMapping.query.all()

        result = []
        for mapping in mappings:
            mapping_data = mapping.to_dict()

            object_uri = mapping_data['object_uri']
            concept_uri = mapping_data['concept_uri']

            object_algs = self.algorithm_mapping_service.get_child_and_parent_algorithm(object_uri)
            concept_algs = self.algorithm_mapping_service.get_child_and_parent_algorithm(concept_uri)

            mapping_data['object_algs'] = object_algs
            mapping_data['concept_algs'] = concept_algs

            result.append(mapping_data)

        return jsonify(result)

    @get_route("/clause/mappings/<clause_id>")
    def get_mapping(self, clause_id):
        mappings = ClauseEntityTypeMapping.query.filter_by(clause_id=clause_id).all()

        result = []
        for mapping in mappings:
            mapping_data = mapping.to_dict()

            object_uri = mapping_data['object_uri']
            concept_uri = mapping_data['concept_uri']

            object_algs = self.algorithm_mapping_service.get_child_and_parent_algorithm(object_uri)
            concept_algs = self.algorithm_mapping_service.get_child_and_parent_algorithm(concept_uri)

            mapping_data['object_algs'] = object_algs
            mapping_data['concept_algs'] = concept_algs

            result.append(mapping_data)

        return jsonify(result)

    @post_route("/clause/mappings")
    def create_mapping(self):
        data = request.json
        result = self.clause_service.create_mapping(data)

        object_uri = result['object_uri']
        concept_uri = result['concept_uri']

        object_algs = self.algorithm_mapping_service.get_child_and_parent_algorithm(object_uri)
        concept_algs = self.algorithm_mapping_service.get_child_and_parent_algorithm(concept_uri)

        result['object_algs'] = object_algs
        result['concept_algs'] = concept_algs

        return jsonify(result)

    @put_route("/clause/mappings/<mapping_id>")
    def update_mapping(self, mapping_id):
        mapping = ClauseEntityTypeMapping.query.filter_by(id=mapping_id).first()
        if mapping is None:
            abort(404)
        data = request.json
        self.clause_service.update_mapping(data, mapping)
        return 'success'

    @delete_route('/clause/mappings/<mapping_id>')
    def delete_mapping(self, mapping_id):
        mapping = ClauseEntityTypeMapping.query.filter_by(id=mapping_id).first()
        if mapping is None:
            abort(404)

        self.clause_service.delete_mapping(mapping)
        return 'success'

    @put_route('/clause/mappings/_checkout_uri')
    def checkout_mapping_uri(self):
        self.clause_service.checkout_mapping_uri()
        return "success"

    @put_route("/clause/_checkout_match_catalog_clause")
    def checkout_match_catalog_clause(self):
        self.clause_service.checkout_match_catalog_clause()
        return "success"

    @post_route("/clause/clauses/upload-file")
    def create_clause_from_file(self):
        file = request.files.get('file')

        if file and allowed_file(file.filename):
            file_path = os.path.join(settings.get('UPLOAD_DIR'), file.filename)
            file.save(file_path)

            status = self.clause_service.create_clause_from_file(file_path)
            return jsonify(status)
        else:
            return "invalid file"

    @post_route("/clause/mappings/upload-file")
    def create_mapping_from_file(self):
        file = request.files.get('file')

        if file and allowed_file(file.filename):
            file_path = os.path.join(settings.get('UPLOAD_DIR'), file.filename)
            file.save(file_path)

            status = self.clause_service.create_mapping_from_file(file_path)
            return jsonify(status)
        else:
            return "invalid file"