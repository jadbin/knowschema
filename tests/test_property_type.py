import requests
import json

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_url = "http://localhost:8062/api/property-types"

param = {
    "uri": "test",
    "display_name": "test",
    "field_type": "INT",
    "is_entity": 0,
    "entity_type_id": 4691
}

headers = {"Content-Type": "application/json"}

property_type_id = 0

def test_create_property_type():
    url = root_url
    data = json.dumps(param)

    response = requests.post(url, data=data, headers=headers)
    logger.debug(response.status_code)
    logger.debug(response.json())

    global property_type_id
    property_type_id = response.json()['id']
    logger.debug(property_type_id)

    assert response.status_code == 200

def test_update_property_type():
    param['description'] = "test update function"
    data = json.dumps(param)

    url = root_url + "/" + str(property_type_id)
    logger.debug(url)
    response = requests.put(url, data=data, headers=headers)
    logger.debug(response.status_code)

    assert response.status_code == 200

def test_delete_property_type():
    url = root_url + "/" + str(property_type_id)
    logger.debug(url)
    response = requests.delete(url, headers=headers)
    logger.debug(response.status_code)

    assert response.status_code == 200