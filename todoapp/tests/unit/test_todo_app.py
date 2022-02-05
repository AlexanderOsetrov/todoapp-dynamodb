import pytest
from flask import json
from copy import deepcopy
from todoapp import create_app, init_db
from todoapp.tests.utils.utils import logger


test_item_body = {
        "title": "test_item",
        "completed": False,
        "order": 1
    }


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        with app.app_context():
            init_db(app)
        yield client
        client.delete("/items")


@pytest.fixture
def test_item(client):
    response = client.post('/items', json=test_item_body)
    logger.info("Item created: %s" % json.loads(response.data))
    return response


def test_add_item(client):  
    response = client.post('/items', json=test_item_body)
    assert response.status == "201 CREATED"
    assert json.loads(response.data).get('title') == test_item_body.get('title')
    assert not json.loads(response.data).get('completed')


def test_edit_item(client, test_item):
    item_id = json.loads(test_item.data).get('id')
    item_order = json.loads(test_item.data).get('order')
    response = client.put(f'/items/{item_id}', json={'title': "test_item_done", 'completed': True, 'order': item_order})
    logger.info("Item updated: %s" % json.loads(response.data))
    assert response.status == "200 OK"
    assert json.loads(response.data).get('title') == "test_item_done"
    assert json.loads(response.data).get('completed')


def test_delete_item(client, test_item):
    item_id = json.loads(test_item.data).get('id')
    response = client.delete(f'/items/{item_id}')
    logger.info("Item deleted: %s" % response.status)
    assert response.status == "204 NO CONTENT"
    response = client.get("/items")
    logger.info(f"Items found: %s" % json.loads(response.data))
    assert not json.loads(response.data)


def test_get_items(client):
    test_item_1 = deepcopy(test_item_body)
    test_item_1['title'] = "item_1"
    test_item_1['order'] = 1
    test_item_2 = deepcopy(test_item_body)
    test_item_2['title'] = "item_2"
    test_item_2['order'] = 2
    client.post('/items', json=test_item_1)
    client.post('/items', json=test_item_2)
    response = client.get("/items")
    logger.info(f"Items found: %s" % json.loads(response.data))
    assert json.loads(response.data)[0].get('title') == "item_1"
    assert json.loads(response.data)[0].get('order') == 1
    assert json.loads(response.data)[1].get('title') == "item_2"
    assert json.loads(response.data)[1].get('order') == 2
