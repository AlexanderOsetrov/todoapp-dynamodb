import json
import random
import string
import pytest
from pytest import fixture
from selenium import webdriver
from requests import Session
from todoapp.tests.bdd.api_resources.items import Items


@fixture(scope="session")
def config():
    try:
        with open("services/web/todoapp/tests/bdd/config.json") as config_file:
            config = json.loads(config_file.read())
            return config
    except FileNotFoundError:
        pytest.skip("Configuration is not found")


@fixture(scope="session")
def app_host(config):
    if config.get("webdriver_remote"):
        return "http://web-dev:5001"
    else:
        return "http://127.0.0.1:5001"


@fixture(scope="function")
def browser(config):
    capabilities = config.get("capabilities")
    remote_host = config.get("selenoid_host")
    if config.get("webdriver_remote"):
        browser = webdriver.Remote(remote_host, capabilities)
    else:
        browser = webdriver.Chrome()
    browser.maximize_window()
    yield browser
    browser.quit()


@fixture(scope="function")
def api_session():
    session = Session()
    yield session
    session.close()


@fixture(scope="function")
def delete_items(config, api_session):
    items_resource = Items(api_session)
    items_resource.add_host(config.get("app_host"))
    yield
    items = items_resource.get_items()
    for item in items:
        items_resource.delete_item(item.get('id'))


@fixture
def context():
    class Context(object):
        pass
    return Context()


@fixture
def random_title():
    random_title = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return random_title


@fixture
def random_todo(api_session, config, random_title):
    items_resource = Items(api_session)
    items_resource.add_host(config.get("app_host"))
    item = {
        "title": random_title,
        "completed": False,
        "order": 1
    }
    response = items_resource.add_item(item)
    return response.json()
