# coding=utf-8

from flask import request, abort, jsonify
from guniflask.web import blueprint, get_route, post_route, put_route, delete_route

from knowschema.models import Field, Book, Catalog, Clause, ClauseEntityTypeMapping, EntityType


@blueprint('/api')
class MainPageController:
    def __init__(self):
        pass

    @get_route("/main-page/stat")
    def get_stat(self):
        # 知识类别数量
        fields = Field.query.all()
        field_num = len(fields)

        # 知识数量
        books = Book.query.all()
        book_num = len(books)

        # 涉及领域数量
        catalogs = Catalog.query.all()
        catalog_num = len(catalogs)

        # 事项数量
        clauses = Clause.query.all()
        clause_num = len(clauses)

        # 普通用户添加概念总数
        entity_types = EntityType.query.all()
        common_user_entity_type_num = {
            "total_entity_type_num": len(entity_types),
            "level_1_num": 0,
            "level_2_num": 0,
            "level_3_num": 0
        }
        level_1_entity_type = EntityType.query.filter_by(father_id=0).all()
        common_user_entity_type_num['level_1_num'] = len(level_1_entity_type)
        level_2_entity_type = [j for i in level_1_entity_type for j in EntityType.query.filter_by(father_id=i.id).all()]
        common_user_entity_type_num['level_2_num'] = len(level_2_entity_type)
        level_3_entity_type = [j for i in level_2_entity_type for j in EntityType.query.filter_by(father_id=i.id).all()]
        common_user_entity_type_num['level_3_num'] = len(level_3_entity_type)

        # 领域专家确认概念总数
        expert_entity_type_num = 0

        # 事项匹配数量 & 事项匹配比例
        mappings = ClauseEntityTypeMapping.query.all()
        has_mapping_clauses = [i.clause_id for i in mappings]
        has_mapping_clauses = list(set(has_mapping_clauses))
        has_mapping_clauses_num = len(has_mapping_clauses)
        has_mapping_clauses_rate = has_mapping_clauses_num / clause_num

        # 知识中事项匹配统计
        def get_field_stat(field):
            relative_clauses = [clause
                                for book in Book.query.filter_by(field_id=field.id).all()
                                for catalog in Catalog.query.filter_by(book_id=book.id).all()
                                for clause in Clause.query.filter_by(catalog_id=catalog.id).all()]
            has_mapping_relative_clauses = [clause
                                            for clause in relative_clauses
                                            if len(ClauseEntityTypeMapping.query.filter_by(clause_id=clause.id).all()) > 0]
            relative_clauses_num = len(relative_clauses)
            has_mapping_relative_clauses_num = len(has_mapping_relative_clauses)
            rate = has_mapping_relative_clauses_num / (relative_clauses_num + 1e-5)
            return {"relative_clauses_num": relative_clauses_num,
                    "has_mapping_relative_clauses_num": has_mapping_relative_clauses_num,
                    "rate": rate}

        clause_per_field_num = {
            field.uri: get_field_stat(field) for field in fields
        }

        # 结果
        result = {
            "field_num": field_num,
            "book_num": book_num,
            "catalog_num": catalog_num,
            "clause_num": clause_num,
            "common_user_entity_type_num": common_user_entity_type_num,
            "expert_entity_type_num": expert_entity_type_num,
            "has_mapping_clauses_num": has_mapping_clauses_num,
            "has_mapping_clauses_rate": has_mapping_clauses_rate,
            "clause_per_field_num": clause_per_field_num
        }

        return jsonify(result)
