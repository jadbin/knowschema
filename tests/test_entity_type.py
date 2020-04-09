import requests
import json

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_url = "http://localhost:8062/api/entity-types"

param = {
    "uri": "refactoring",
    "display_name": "refactoring",
    "father_id": 4691,
    "is_object": 1,
}

headers = {"Content-Type": "application/json"}

entity_type_id = 0
copy_entity_type_id = 0

def test_create_entity_type():
    url = root_url
    data = json.dumps(param)

    response = requests.post(url, data=data, headers=headers)
    logger.debug(f"Status : {response.status_code}")
    logger.debug(response.text)

    if response.status_code == 200:
        global entity_type_id
        entity_type_id = response.json()['id']
        logger.debug(entity_type_id)

    assert response.status_code == 200

def test_update_clause_mapping():
    param['father_id'] = 4695
    data = json.dumps(param)

    url = root_url + "/" + str(entity_type_id)
    logger.debug(url)
    response = requests.put(url, data=data, headers=headers)
    logger.debug(response.status_code)

    assert response.status_code == 200

def test_delete_entity_type():
    url = root_url + "/" + str(entity_type_id)
    logger.debug(url)
    response = requests.delete(url, headers=headers)
    logger.debug(response.status_code)

    assert response.status_code == 200

def test_copy_entity_type():
    param = {"uri": "test for copy"}
    data = json.dumps(param)

    url = root_url + "/copy/" + str(4702)
    logger.debug(url)
    response = requests.put(url, data=data, headers=headers)
    logger.debug(response.status_code)
    assert response.status_code == 200
    global copy_entity_type_id
    copy_entity_type_id = response.json()['id']
    logger.debug(copy_entity_type_id)

def test_merge_entity_type():
    url = root_url + "/merge/" + str(copy_entity_type_id) + "/" + str(4702)
    logger.debug(url)
    response = requests.put(url, headers=headers)
    logger.debug(response.status_code)
    assert response.status_code == 200

def test_set_meta_type():
    for i in [3983, 3984, 3985, 3986]:
        url = root_url + "/set-object/" + str(i)
        logger.debug(url)
        response = requests.put(url, headers=headers)
        logger.debug(response.status_code)
        assert response.status_code == 200

def test_checkout_child():
    url = root_url + "/_checkout_child"
    logger.debug(url)
    response = requests.put(url, headers=headers)
    logger.debug(response.status_code)
    assert response.status_code == 200