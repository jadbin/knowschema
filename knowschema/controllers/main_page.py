# coding=utf-8

import logging
import time

from flask import request, jsonify
from guniflask.web import blueprint, get_route, post_route

from knowschema.models import Field, Book, Catalog, Clause, ClauseEntityTypeMapping, EntityType

log = logging.getLogger(__name__)


@blueprint('/api')
class MainPageController:
    def __init__(self):
        self.cache_stat = None
        self.last_time = None
        pass

    def get_statistics(self):
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
            "total_entity_type_num": 0,
            "level_1_num": 0,
            "level_2_num": 0,
            "level_3_num": 0,
            "object_level_1_num": 0,
            "object_level_2_num": 0,
            "object_level_3_num": 0,
            "concept_level_1_num": 0,
            "concept_level_2_num": 0,
            "concept_level_3_num": 0,
        }
        level_1_entity_type = EntityType.query.filter_by(father_id=0).all()
        common_user_entity_type_num['level_1_num'] = len(level_1_entity_type)
        common_user_entity_type_num['object_level_1_num'] = len([i for i in level_1_entity_type if i.is_object == 1])
        common_user_entity_type_num['concept_level_1_num'] = len([i for i in level_1_entity_type if i.is_object == 0])

        level_2_entity_type = [j for i in level_1_entity_type for j in EntityType.query.filter_by(father_id=i.id).all()]
        common_user_entity_type_num['level_2_num'] = len(level_2_entity_type)
        common_user_entity_type_num['object_level_2_num'] = len([i for i in level_2_entity_type if i.is_object == 1])
        common_user_entity_type_num['concept_level_2_num'] = len([i for i in level_2_entity_type if i.is_object == 0])

        level_3_entity_type = [j for i in level_2_entity_type for j in EntityType.query.filter_by(father_id=i.id).all()]
        common_user_entity_type_num['level_3_num'] = len(level_3_entity_type)
        common_user_entity_type_num['object_level_3_num'] = len([i for i in level_3_entity_type if i.is_object == 1])
        common_user_entity_type_num['concept_level_3_num'] = len([i for i in level_3_entity_type if i.is_object == 0])

        common_user_entity_type_num['total_entity_type_num'] = common_user_entity_type_num['level_1_num'] + \
                                                               common_user_entity_type_num['level_2_num'] + \
                                                               common_user_entity_type_num['level_3_num']

        for entity_type in entity_types:
            if entity_type not in level_1_entity_type and entity_type not in level_2_entity_type and entity_type not in level_3_entity_type:
                log.warning(f"Warning entity type : {entity_type.id}")

        # 领域专家确认概念总数
        expert_entity_type_num = 0

        # 事项匹配数量 & 事项匹配比例
        mappings = ClauseEntityTypeMapping.query.all()

        all_mappings = [i.clause_id for i in mappings]
        all_mappings_clauses_list = list(set(all_mappings))
        all_mappings_clauses_num = len(all_mappings_clauses_list)
        all_clauses = [i.id for i in clauses]
        first_non_mapping_clauses_list = [i for i in all_clauses if i not in all_mappings_clauses_list]
        first_non_mapping_clauses_num = clause_num - all_mappings_clauses_num

        has_mapping_clauses = set([i.clause_id for i in mappings if i.concept_id is not None])
        non_concept_in_mapping_clauses = set([i.clause_id for i in mappings if i.concept_id is None])
        second_non_mapping_clauses_list = list(non_concept_in_mapping_clauses - has_mapping_clauses)
        second_non_mapping_clauses_num = len(second_non_mapping_clauses_list)

        has_mapping_clauses_num = clause_num - first_non_mapping_clauses_num - second_non_mapping_clauses_num
        has_mapping_clauses_rate = has_mapping_clauses_num / clause_num
        non_mapping_clauses_list = first_non_mapping_clauses_list + second_non_mapping_clauses_list
        non_mapping_clauses_list = [Clause.query.filter_by(id=i).first().uri for i in non_mapping_clauses_list]

        # 知识中事项匹配统计
        def get_field_stat(field):
            relative_clauses = [clause
                                for book in Book.query.filter_by(field_id=field.id).all()
                                for catalog in Catalog.query.filter_by(book_id=book.id).all()
                                for clause in Clause.query.filter_by(catalog_id=catalog.id).all()]
            has_mapping_relative_clauses = [clause
                                            for clause in relative_clauses
                                            if len(ClauseEntityTypeMapping.query
                                                   .filter_by(clause_id=clause.id)
                                                   .filter(ClauseEntityTypeMapping.concept_uri != None).all()) > 0]
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
            "clause_per_field_num": clause_per_field_num,
            "non_mapping_clauses_list": non_mapping_clauses_list
        }

        return result

    @get_route("/main-page/stat")
    def get_stat(self):
        result = self.get_statistics()
        return jsonify(result)

    @post_route("/main-page/search")
    def search(self):
        key_word = request.json.get('query')
        results = {}

        entity_types_by_uri = EntityType.query.filter(EntityType.uri.like("%" + key_word + "%")).all()
        entity_types_by_description = EntityType.query.filter(EntityType.description.like("%" + key_word + "%")).all()
        entity_types = list(set(entity_types_by_uri + entity_types_by_description))
        results['entity-types'] = [i.to_dict() for i in entity_types]

        # property_types_by_uri = PropertyType.query.filter(PropertyType.uri.like("%" + key_word + "%")).all()
        # property_types_by_description = PropertyType.query.filter(PropertyType.description.like("%" + key_word + "%")).all()
        # property_types = list(set(property_types_by_uri + property_types_by_description))
        # results['property-types'] = [i.to_dict() for i in property_types]
        #
        # fields_by_uri = Field.query.filter(Field.uri.like("%" + key_word + "%")).all()
        # fields_by_description = Field.query.filter(Field.description.like("%" + key_word + "%")).all()
        # fields = list(set(fields_by_uri + fields_by_description))
        # results['fields'] = [i.to_dict() for i in fields]
        #
        # books_by_uri = Book.query.filter(Book.uri.like("%" + key_word + "%")).all()
        # books_by_description = Book.query.filter(Book.description.like("%" + key_word + "%")).all()
        # books = list(set(books_by_uri + books_by_description))
        # results['books'] = [i.to_dict() for i in books]
        #
        # catalogs_by_uri = Catalog.query.filter(Catalog.uri.like("%" + key_word + "%")).all()
        # catalogs_by_description = Catalog.query.filter(Catalog.description.like("%" + key_word + "%")).all()
        # catalogs = list(set(catalogs_by_uri + catalogs_by_description))
        # results['catalogs'] = [i.to_dict() for i in catalogs]
        #
        # clauses_by_uri = Clause.query.filter(Clause.uri.like("%" + key_word + "%")).all()
        # clauses_by_content = Clause.query.filter(Clause.content.like("%" + key_word + "%")).all()
        # clauses = list(set(clauses_by_uri + clauses_by_content))
        # results['clauses'] = [i.to_dict() for i in clauses]
        #
        # mappings_by_uri = ClauseEntityTypeMapping.query.filter(ClauseEntityTypeMapping.uri.like("%" + key_word + "%")).all()
        # mappings_by_description = ClauseEntityTypeMapping.query.filter(ClauseEntityTypeMapping.description.like("%" + key_word + "%")).all()
        # mappings = list(set(mappings_by_uri + mappings_by_description))
        # results['mappings'] = [i.to_dict() for i in mappings]

        return jsonify(results)

    @get_route("/main-page/stats-for-nuwa")
    def get_stats_for_nuwa(self):
        def stat():
            result = {
                "unhandled_items": None,
                "fields_count": None,
                "items_count": None,
                "concept_count": None,
                "regulation_count": None
            }

            stat = self.get_statistics()

            result["unhandled_items"] = len(stat["non_mapping_clauses_list"])
            result["items_count"] = stat["clause_num"]
            result["regulation_count"] = stat["book_num"]
            result["concept_count"] = stat["common_user_entity_type_num"]["total_entity_type_num"]

            field_num = 0

            field_parent = EntityType.query.filter_by(uri="领域").first()
            field_parent_id = field_parent.id

            fields = EntityType.query.filter_by(father_id=field_parent_id).all()
            for field in fields:
                field_id = field.id
                sub_fields = EntityType.query.filter_by(father_id=field_id).all()

                field_num += len(sub_fields)

            result["fields_count"] = field_num

            return result

        current_time = time.time()
        if self.cache_stat is None or (current_time - self.last_time) > 86400:
            result = stat()
            self.cache_stat = result
            self.last_time = time.time()
            return jsonify(result)
        else:
            return jsonify(self.cache_stat)
