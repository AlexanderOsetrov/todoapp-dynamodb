from todoapp.models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, render_template
from todoapp.app_setup import verify_authentication


main = Blueprint('main', __name__)


@main.route('/')
def index():
    verify_authentication()
    return render_template('index.html')


@main.route('/todos')
@jwt_required(refresh=True)
def todos():
    verify_authentication()
    uid = get_jwt_identity()
    user = UserModel.find_user_by_uid(uid)
    return render_template('todos.html', todos=user['items'], uid=user['uid'])
