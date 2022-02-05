from asyncio.log import logger
import json
import logging
from logging.config import dictConfig
from flask import Flask, render_template
from flask_cors import CORS
from flask_restful import Api
from todoapp.dynamo import create_or_get_table
from todoapp.resources.item import Item, ItemList


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s\t[%(name)s.%(funcName)s:%(lineno)d.%(levelname)s]\t%(message)s',
        'datefmt' : '%b %d %H:%M:%S'
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'}
            },
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})


def get_app_version():
    try:
        with open("todoapp/app_version.json", "r") as version_file:
            version_json = json.loads(version_file.read())
            return version_json.get('version', 'unknown')
    except FileNotFoundError:
        return "unknown"


def create_app():
    flask_app = Flask(__name__, static_url_path='')
    api = Api(flask_app)
    CORS(flask_app)
    api.add_resource(ItemList, '/items', endpoint="items")
    api.add_resource(Item, '/items/<item_id>')
    
    @flask_app.before_first_request
    def create_tables():
        create_or_get_table()

    @flask_app.route('/')
    def index():
        todos = ItemList().get()
        app_version = get_app_version()
        return render_template('index.html', todos=todos, app_version=app_version)
    return flask_app


app = create_app()
