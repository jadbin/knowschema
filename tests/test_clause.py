import requests
import json

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

root_url = "http://localhost:8062/api/clause"

headers = {"Content-Type": "application/json"}

def test_update_field():
    url = root_url + "/fields/" + str(1)
    param = {
        "count": 2,
        "support": "sss",
        "description": "ddd"
    }
    data = json.dumps(param)

    response = requests.put(url, data=data, headers=headers)
    logger.debug(response.status_code)
    assert response.status_code == 200
    logger.debug(response.json())

def test_update_book():
    url = root_url + "/books/" + str(1)
    param = {
        "public_org": "org",
        "description": "ddd"
    }
    data = json.dumps(param)

    response = requests.put(url, data=data, headers=headers)
    logger.debug(response.status_code)
    assert response.status_code == 200
    logger.debug(response.json())

def test_update_catalog():
    url = root_url + "/catalogs/" + str(1)
    param = {
        "title": "ttt",
        "number": "4548593405",
        "description": "ddd",
        "text": "tttttt"
    }
    data = json.dumps(param)

    response = requests.put(url, data=data, headers=headers)
    logger.debug(response.status_code)
    assert response.status_code == 200
    logger.debug(response.json())

def test_update_clause():
    url = root_url + "/clauses/" + str(1080)
    param = {
        "level": 3,
        "content": "ccc",
        "insider": "ppppppppppp"
    }
    data = json.dumps(param)

    response = requests.put(url, data=data, headers=headers)
    logger.debug(response.status_code)
    assert response.status_code == 200
    logger.debug(response.json())