import logging

from guniflask.web import blueprint, post_route
from guniflask.scheduling import scheduled

from knowschema.services.graph_sync import GraphSyncService

log = logging.getLogger(__name__)


@blueprint('/api')
class GraphSyncController:
    def __init__(self, graph_sync_service: GraphSyncService):
        self.graph_sync_service = graph_sync_service

    @post_route('/graph-sync')
    def sync_all(self):
        """
        手动备份
        """
        with self.graph_sync_service.session() as session:
            """
            组装节点和关系
            """
            # TODO
            # session.add_entity()
            # session.add_relation()

    @scheduled(interval=5 * 60)
    def scheduled_sync_all(self):
        """
        5分钟同步一次
        """
        self.sync_all()
