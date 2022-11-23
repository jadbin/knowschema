# coding=utf-8

import logging

from flask import jsonify
from guniflask.web import blueprint, get_route

from knowschema.models import OperationRecord

log = logging.getLogger(__name__)


@blueprint('/api')
class OperationRecordController:
    def __init__(self):
        pass

    @get_route('/operation-records/<entity_type_id>')
    def get_operation_record(self, entity_type_id):
        operation_records = OperationRecord.query.filter_by(entity_type_id=entity_type_id)
        result = []
        for record in operation_records:
            d = record.to_dict()
            result.append(d)
        return jsonify(result)
