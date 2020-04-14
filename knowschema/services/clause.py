# coding=utf-8

import logging

from guniflask.context import service
from sqlalchemy import exc

from knowschema.models import Field, Book, Catalog, Clause, ClauseEntityTypeMapping, EntityType
from knowschema.services.operation_record import OperationRecordService
from knowschema.app import db

log = logging.getLogger(__name__)

@service
class ClauseService:

    def __init__(self, operation_record_service: OperationRecordService):
        self.operation_record_service = operation_record_service

    def create_field(self, data, operator="admin"):
        field = Field.from_dict(data, ignore='id,created_at,updated_at')
        try:
            db.session.add(field)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI"
        else:
            self.operation_record_service.create_field_record(operator, field)
            return field.to_dict()

    def update_field(self, data, field, operator="admin"):
        original_data = field.to_dict()
        try:
            field.update_by_dict(data, ignore="id")
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI"
        else:
            self.operation_record_service.update_field_record(operator, data, original_data)
            return field.to_dict()

    def delete_field(self, field, operator="admin"):
        self.operation_record_service.delete_field_record(operator, field)
        data = field.to_dict()
        db.session.delete(field)
        db.session.commit()
        return data

    def create_book(self, data, operator="admin"):
        book = Book.from_dict(data, ignore='id,created_at,updated_at')
        try:
            db.session.add(book)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI"
        else:
            self.operation_record_service.create_book_record(operator, book)
            return book.to_dict()

    def update_book(self, data, book, operator="admin"):
        original_data = book.to_dict()
        try:
            book.update_by_dict(data, ignore="id")
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI"
        else:
            self.operation_record_service.update_book_record(operator, data, original_data)
            return book.to_dict()

    def delete_book(self, book, operator="admin"):
        self.operation_record_service.delete_book_record(operator, book)
        data = book.to_dict()
        db.session.delete(book)
        db.session.commit()
        return data

    def create_catalog(self, data, operator="admin"):
        catalog = Catalog.from_dict(data, ignore='id,created_at,updated_at')
        try:
            db.session.add(catalog)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI"
        else:
            self.operation_record_service.create_catalog_record(operator, catalog)
            return catalog.to_dict()

    def update_catalog(self, data, catalog, operator="admin"):
        original_data = catalog.to_dict()
        try:
            catalog.update_by_dict(data, ignore="id")
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI"
        else:
            self.operation_record_service.update_catalog_record(operator, data, original_data)
            return catalog.to_dict()

    def delete_catalog(self, catalog, operator="admin"):
        self.operation_record_service.delete_catalog_record(operator, catalog)
        data = catalog.to_dict()
        db.session.delete(catalog)
        db.session.commit()
        return data

    def create_clause(self, data, operator="admin"):
        clause = Clause.from_dict(data, ignore='id,created_at,updated_at')
        try:
            db.session.add(clause)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI"
        else:
            self.operation_record_service.create_clause_record(operator, clause)
            return clause.to_dict()

    def update_clause(self, data, clause, operator="admin"):
        original_data = clause.to_dict()
        try:
            clause.update_by_dict(data, ignore="id")
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return "重复URI"
        else:
            self.operation_record_service.update_clause_record(operator, data, original_data)

            if data.get('uri') is not None and data['uri'] != original_data['uri']:
                mappings = ClauseEntityTypeMapping.query.filter_by(clause_id=clause.id).all()
                for mapping in mappings:
                    mapping_data = mapping.to_dict()
                    mapping_data['clause_uri'] = data['uri']
                    self.update_clause_mapping(mapping_data, mapping, operator)

            return clause.to_dict()

    def delete_clause(self, clause, operator="admin"):
        self.operation_record_service.delete_clause_record(operator, clause)
        data = clause.to_dict()
        db.session.delete(clause)
        db.session.commit()
        return data

    def create_mapping(self, data, operator="admin"):
        mapping = ClauseEntityTypeMapping.from_dict(data, ignore='id,created_at,updated_at')

        db.session.add(mapping)
        db.session.commit()

        self.operation_record_service.create_clause_mapping_record(operator, mapping)

        return mapping.to_dict()

    def update_mapping(self, data, mapping, operator="admin"):
        self.operation_record_service.update_clause_mapping_record(operator, data, mapping)

        mapping.update_by_dict(data, ignore='id,create_at,updated_at')
        db.session.commit()

        return mapping.to_dict()

    def delete_mapping(self, mapping, operator="admin"):
        self.operation_record_service.delete_clause_mapping_record(operator, mapping)

        data = mapping.to_dict()

        db.session.delete(mapping)
        db.session.commit()

        return data

    def checkout_mapping_uri(self):
        operator = "admin"

        mappings = ClauseEntityTypeMapping.query.all()
        for mapping in mappings:
            clause = Clause.query.filter_by(id=mapping.clause_id).first()
            if clause is None:
                log.warning(f"Error clause id : {mapping.clause_id}")
                clause_uri = "(缺失)"
            else:
                clause_uri = clause.uri

            obj = EntityType.query.filter_by(id=mapping.object_id).first()
            if obj is None:
                log.warning(f"Error object id : {mapping.object_id}")
                object_uri = "(缺失)"
            else:
                object_uri = obj.uri

            concept = EntityType.query.filter_by(id=mapping.concept_id).first()
            if concept is None:
                log.warning(f"Error concept id : {mapping.concept_id}")
                concept_uri = "(缺失)"
            else:
                concept_uri = concept.uri

            data = mapping.to_dict()
            data['clause_uri'] = clause_uri
            data['object_uri'] = object_uri
            data['concept_uri'] = concept_uri

            self.operation_record_service.update_clause_mapping_record(operator, data, mapping)

            mapping.update_by_dict(data, ignore='id,create_at,updated_at')
        db.session.commit()

    def checkout_match_catalog_clause(self):
        from pypinyin import lazy_pinyin

        catalogs = Catalog.query.all()
        for catalog in catalogs:
            data = catalog.to_dict()

            name = catalog.uri
            if name[-2:] == "工作":
                name = name[:-2]
            pinyin = lazy_pinyin(name)
            pinyin = "".join(pinyin)

            data['description'] = pinyin

            self.update_catalog(data, catalog)

        clauses = Clause.query.all()
        catalogs = Catalog.query.all()
        for clause in clauses:
            clause_data = clause.to_dict()

            for catalog in catalogs:
                if catalog.description in clause.uri:
                    clause_data['catalog_id'] = catalog.id
                    self.update_clause(clause_data, clause)
                    break