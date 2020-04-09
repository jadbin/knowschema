import requests
import json

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_url = "http://localhost:8062/api/clause"

param = {
    "clause_id": 934,
    "object_id": 4087,
    "concept_id": 4242
}

headers = {"Content-Type": "application/json"}

mapping_id = 0

def test_create_mapping():
    url = root_url + "/mappings"
    data = json.dumps(param)

    response = requests.post(url, data=data, headers=headers)
    logger.debug(response.status_code)
    logger.debug(response.json())

    global mapping_id
    mapping_id = response.json()['id']
    logger.debug(mapping_id)

    assert response.status_code == 200

def test_update_mapping():
    param['description'] = "test update function"
    data = json.dumps(param)

    url = root_url + "/mappings/" + str(mapping_id)
    logger.debug(url)
    response = requests.put(url, data=data, headers=headers)
    logger.debug(response.status_code)

    assert response.status_code == 200

def test_delete_mapping():
    url = root_url + "/mappings/" + str(mapping_id)
    logger.debug(url)
    response = requests.delete(url, headers=headers)
    logger.debug(response.status_code)

    assert response.status_code == 200

def test_checkout_mapping_uri():
    url = root_url + "/mapping/_checkout_mapping_uri"
    logger.debug(url)
    response = requests.put(url, headers=headers)
    logger.debug(response.status_code)

    assert response.status_code == 200