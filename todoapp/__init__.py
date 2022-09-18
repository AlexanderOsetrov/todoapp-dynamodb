from flask import Flask
from flask_restful import Api
from todoapp.dynamo import create_or_get_table
from flask_jwt_extended import JWTManager
from todoapp.app_setup import set_app_config, register_api_resources, create_default_admin


def create_app():
    flask_app = Flask(__name__, static_url_path='')
    set_app_config(flask_app)
    api = Api(flask_app)
    register_api_resources(api)
    jwt = JWTManager(flask_app)
    from todoapp.views.auth import auth as auth_blueprint
    from todoapp.views.main import main as main_blueprint
    from todoapp.views.settings import settings as settings_blueprint
    flask_app.register_blueprint(auth_blueprint)
    flask_app.register_blueprint(main_blueprint)
    flask_app.register_blueprint(settings_blueprint)
    create_or_get_table()
    create_default_admin(flask_app)
    return flask_app


app = create_app()
