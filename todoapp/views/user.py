from todoapp.models.user import UserModel
from flask_jwt_extended import jwt_required
from flask import Blueprint, render_template, redirect, url_for, current_app, flash, request
from todoapp.app_setup import verify_authentication
from werkzeug.security import generate_password_hash


user = Blueprint('user', __name__)


@user.route('/users/<uid>')
@jwt_required(refresh=True)
def edit_user(uid):
    verify_authentication()
    _user = UserModel.find_user_by_uid(uid)
    return render_template('user.html', email=_user.email, name=_user.name, uid=_user.uid)


@user.route('/users/<uid>/delete')
@jwt_required(refresh=True)
def delete_user(uid):
    verify_authentication()
    _user = UserModel.find_user_by_uid(uid)
    if _user.name == 'admin':
        flash('Admin user cannot be deleted!')
        return redirect(url_for('settings.get_settings'))
    current_app.logger.info("Removing user: %s" % _user.json())
    _user.delete_from_db()
    return redirect(url_for("settings.get_settings"))


@user.route('/users/<uid>/edit', methods=['POST'])
@jwt_required(refresh=True)
def update_user(uid):
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    _user = UserModel.find_user_by_email(email)
    if user and uid != _user.uid:
        flash('Email address already exists!')
        return redirect(url_for('settings.edit_user', uid=uid))
    edited_user = UserModel.find_user_by_uid(uid)
    edited_user.name = name
    edited_user.email = email
    if password != "":
        edited_user.password = generate_password_hash(password)
    edited_user.save_user_to_db()
    return redirect(url_for("settings.get_settings"))
