from todoapp.models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, render_template, redirect, url_for, current_app, flash, request
from todoapp.app_setup import verify_authentication
from werkzeug.security import generate_password_hash


settings = Blueprint('settings', __name__)


@settings.route('/settings')
@jwt_required(refresh=True)
def get_settings():
    verify_authentication()
    user = UserModel.find_user_by_uid(get_jwt_identity())
    if user.name != 'admin':
        return redirect(url_for("main.index"))
    users = [user for user in UserModel.get_all()]
    items = []
    for user in users:
        for item in user.items:
            item['username'] = user.name
            items.append(item)
    return render_template('settings.html', users=users, items=items)
