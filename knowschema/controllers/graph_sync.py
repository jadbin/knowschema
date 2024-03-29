import json
import logging

from flask import abort, jsonify
from guniflask.config import settings
from guniflask.scheduling import scheduled
from guniflask.web import blueprint, post_route, get_route

from knowschema.models import Clause, Catalog, Book, Field, EntityType, ClauseEntityTypeMapping
from knowschema.services.graph_sync import GraphSyncService
from knowschema.utils.unique_scheduled import unique_process

log = logging.getLogger(__name__)


@blueprint('/api')
class GraphSyncController:
    def __init__(self, graph_sync_service: GraphSyncService):
        self.graph_sync_service = graph_sync_service

    @post_route('/graph-sync')
    @unique_process
    def sync_all(self):
        """
        手动备份
        """
        entities = []
        relations = []

        with self.graph_sync_service.session() as session:
            """
            组装节点和关系
            """
            # TODO: Add entities
            # add clause
            clauses = Clause.query.all()
            for clause in clauses:
                data = {}
                data['local_id'] = "Clause:" + clause.uri
                data['entity_type'] = "保密事项"
                data['entity_name'] = clause.uri
                data['properties'] = {
                    "事项编号": clause.uri,
                    "事项内容": clause.content,
                    "密级": clause.level,
                    "保密期限": clause.time_limit,
                    "知悉范围": clause.insider,
                }

                catalog = Catalog.query.filter_by(id=clause.catalog_id).first()
                if catalog is None:
                    print(clause.id, clause.uri)
                    abort(404)
                data['properties']["领域"] = catalog.uri
                book = Book.query.filter_by(id=catalog.book_id).first()
                data['properties']["知识来源"] = book.uri
                field = Field.query.filter_by(id=book.field_id).first()
                data['properties']["知识类别"] = field.uri

                session.add_entity(**data)
                entities.append(data)

            # add entity type
            entity_types = EntityType.query.all()
            for entity_type in entity_types:
                data = {}
                if entity_type.is_object == 1:
                    data['local_id'] = "Object:" + entity_type.uri
                    data['entity_type'] = "保密对象"
                else:
                    data['local_id'] = "Concept:" + entity_type.uri
                    data['entity_type'] = "保密内容"
                data['entity_name'] = entity_type.uri
                data['properties'] = {}
                for property_type in entity_type.property_types:
                    if property_type.is_entity == 0:
                        data['properties'][property_type.uri] = property_type.field_type

                session.add_entity(**data)
                entities.append(data)

            # TODO: Add relations
            # is_a relation
            entity_types = EntityType.query.all()
            for child in entity_types:
                if child.father_id != 0:
                    parent = EntityType.query.filter_by(id=child.father_id).first()
                    if parent is None:
                        log.warning(f"Parent is None. child : {child.id}, parent : {child.father_id}")
                        continue

                    data = {}
                    if parent.is_object == 1:
                        data['head_local_id'] = "Object:" + parent.uri
                    else:
                        data['head_local_id'] = "Concept:" + parent.uri
                    if child.is_object == 1:
                        data['tail_local_id'] = "Object:" + child.uri
                    else:
                        data['tail_local_id'] = "Concept:" + child.uri
                    data['relation_type'] = "is_a"

                    session.add_relation(**data)
                    relations.append(data)

            # property
            entity_types = EntityType.query.all()
            for head_entity_type in entity_types:
                for property_type in head_entity_type.property_types:
                    if property_type.is_entity == 1:
                        data = {}
                        if head_entity_type.is_object == 1:
                            data['head_local_id'] = "Object:" + head_entity_type.uri
                        else:
                            data['head_local_id'] = "Concept:" + head_entity_type.uri

                        tail_entity_type = EntityType.query.filter_by(uri=property_type.field_type).first()
                        if tail_entity_type is None:
                            continue
                        if tail_entity_type.is_object == 1:
                            data['tail_local_id'] = "Object:" + tail_entity_type.uri
                        else:
                            data['tail_local_id'] = "Concept:" + tail_entity_type.uri
                        data['relation_type'] = property_type.uri

                        session.add_relation(**data)
                        relations.append(data)

            # clause
            argument_entities = []
            argument_relations = []
            mappings = ClauseEntityTypeMapping.query.all()
            for mapping in mappings:
                clause = Clause.query.filter_by(id=mapping.clause_id).first()
                obj = EntityType.query.filter_by(id=mapping.object_id).first()
                concept = EntityType.query.filter_by(id=mapping.concept_id).first()

                if clause is None or obj is None or concept is None:
                    # log.warning(f"{clause}, {obj}, {concept}")
                    continue
                if obj.is_object == 0 or concept.is_object == 1:
                    log.warning(f"{obj} : {obj.uri}, {obj.is_object}, {concept} : {concept.uri}, {concept.is_object}")
                    continue
                else:
                    # 包含事项
                    data = {}
                    data['head_local_id'] = "Object:" + obj.uri
                    data['tail_local_id'] = "Clause:" + clause.uri
                    data['relation_type'] = "包含事项"
                    session.add_relation(**data)
                    relations.append(data)

                    data = {}
                    data['head_local_id'] = "Concept:" + concept.uri
                    data['tail_local_id'] = "Clause:" + clause.uri
                    data['relation_type'] = "包含事项"
                    session.add_relation(**data)
                    relations.append(data)

                    # 保密对象
                    data = {}
                    data['head_local_id'] = "Clause:" + clause.uri
                    data['tail_local_id'] = "Object:" + obj.uri
                    data['relation_type'] = "保密对象"
                    session.add_relation(**data)
                    relations.append(data)

                    # 保密内容
                    data = {}
                    data['head_local_id'] = "Clause:" + clause.uri
                    data['tail_local_id'] = "Concept:" + concept.uri
                    data['relation_type'] = "保密内容"
                    session.add_relation(**data)
                    relations.append(data)

                    # 事项组合
                    data = {}
                    data['head_local_id'] = "Object:" + obj.uri
                    data['tail_local_id'] = "Concept:" + concept.uri
                    data['relation_type'] = "事项组合"
                    session.add_relation(**data)
                    relations.append(data)

                    # 事项论元
                    if mapping.object_name is not None:
                        # 保密事项论元
                        data = {}
                        data['local_id'] = "Argument:" + mapping.object_name
                        data['entity_type'] = "保密事项论元"
                        data['entity_name'] = mapping.object_name
                        data['properties'] = {
                            "保密对象": mapping.object_uri,
                            "事项内容": mapping.concept_uri,
                        }
                        argument_entities.append(data)

                        # 事项与论元关系
                        data = {}
                        data['head_local_id'] = "Clause:" + clause.uri
                        data['tail_local_id'] = "Argument:" + mapping.object_name
                        data['relation_type'] = "包含论元"
                        argument_relations.append(data)

                        data = {}
                        data['head_local_id'] = "Argument:" + mapping.object_name
                        data['tail_local_id'] = "Clause:" + clause.uri
                        data['relation_type'] = "包含事项"
                        argument_relations.append(data)

                    if mapping.concept_name is not None:
                        # 保密事项论元
                        data = {}
                        data['local_id'] = "Argument:" + mapping.concept_name
                        data['entity_type'] = "保密事项论元"
                        data['entity_name'] = mapping.concept_name
                        data['properties'] = {
                            "保密对象": mapping.object_uri,
                            "事项内容": mapping.concept_uri,
                        }
                        argument_entities.append(data)

                        # 事项与论元关系
                        data = {}
                        data['head_local_id'] = "Clause:" + clause.uri
                        data['tail_local_id'] = "Argument:" + mapping.concept_name
                        data['relation_type'] = "包含论元"
                        argument_relations.append(data)

                        data = {}
                        data['head_local_id'] = "Argument:" + mapping.concept_name
                        data['tail_local_id'] = "Clause:" + clause.uri
                        data['relation_type'] = "包含事项"
                        argument_relations.append(data)

        # TODO: Backup graph
        backup_entities = entities + argument_entities
        backup_relations = relations + argument_relations
        backup_data = [backup_entities, backup_relations]

        backup_file = settings.get("GRAPH_BACKUP_FILE")
        with open(backup_file, "w") as f:
            json.dump(backup_data, f, ensure_ascii=False)

        return "success"

    # @unique_scheduled(cron="59 23 * * *")
    @scheduled(cron="59 23 * * *")
    def scheduled_sync_all(self):
        """
        5分钟同步一次
        """
        if settings.get('development') == True:
            log.debug("Development mode. Not sync")
        else:
            log.debug("Syncing schema to graph...")
            self.sync_all()
            log.debug("Synced over.")

    @get_route("/graph-backup")
    def get_graph_backup(self):
        self.sync_all()

        backup_file = settings.get("GRAPH_BACKUP_FILE")
        backup_graph = json.load(open(backup_file))

        return jsonify(backup_graph)
