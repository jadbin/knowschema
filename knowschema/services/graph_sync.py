# coding=utf-8

import logging
from threading import Lock

import requests

from guniflask.context import service
from guniflask.config import settings

log = logging.getLogger(__name__)


class GraphSyncSession:
    def __init__(self, sync_lock):
        self.sync_lock = sync_lock
        self.base_url = settings['elastic_graph_base_url']
        self.session = requests.Session()

        self.entities = []
        self.relations = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def commit(self):
        """
        提交备份
        """
        with self.sync_lock:
            if self.entities or self.relations:
                self._do_commit()

    def _do_commit(self):
        """
        发起具体请求
        1. 删除所有数据
        2. 批量插入节点
        3. 批量插入关系
        """
        self._delete_all()
        self._create_all_entities()
        self.entities = []
        self._create_all_relations()
        self.relations = []

    def _delete_all(self):
        resp = self.session.delete('{}/entities/_all'.format(self.base_url))
        assert resp.status_code == 200, resp.text

    def _create_all_entities(self):
        resp = self.session.post('{}/_bulk/entities'.format(self.base_url), json=self.entities)
        assert resp.status_code == 200, resp.text

    def _create_all_relations(self):
        resp = self.session.post('{}/_bulk/relations?by_local=True'.format(self.base_url), json=self.relations)
        assert resp.status_code == 200, resp.text

    def close(self):
        self.commit()

    def add_entity(self, local_id: str = None, entity_type: str = None, entity_name: str = None,
                   properties: dict = None):
        self.entities.append(dict(local_id=local_id,
                                  entity_type=entity_type,
                                  entity_name=entity_name,
                                  properties=properties))

    def add_relation(self, head_local_id: str = None, relation_type: str = None, tail_local_id: str = None):
        data = {
            'head_entity_id': head_local_id,
            'tail_entity_id': tail_local_id,
            'relation_type': relation_type
        }
        self.relations.append(data)


@service
class GraphSyncService:
    def __init__(self):
        self.sync_lock = Lock()

    def session(self) -> GraphSyncSession:
        return GraphSyncSession(self.sync_lock)
