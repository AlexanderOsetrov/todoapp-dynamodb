from flask import Flask
from flask_restful import Api
from todoapp.dynamo import create_or_get_table
from flask_jwt_extended import JWTManager
from todoapp.app_setup import set_app_config, register_api_resources, create_default_admin, register_blueprints
from flask.logging import default_handler


def create_app():
    flask_app = Flask(__name__, static_url_path='', static_folder='static')
    flask_app.logger.removeHandler(default_handler)
    set_app_config(flask_app)
    api = Api(flask_app)
    register_api_resources(api)
    register_blueprints(flask_app)
    jwt = JWTManager(flask_app)
    create_or_get_table()
    create_default_admin(flask_app)
    return flask_app


app = create_app()
