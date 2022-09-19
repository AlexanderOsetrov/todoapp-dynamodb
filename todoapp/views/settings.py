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


@settings.route('/settings/user/<uid>/delete')
@jwt_required(refresh=True)
def delete_user(uid):
    verify_authentication()
    user = UserModel.find_user_by_uid(uid)
    if user.name == 'admin':
        flash('Admin user cannot be deleted!')
        return redirect(url_for('settings.get_settings'))
    current_app.logger.info("Removing user: %s" % user.json())
    user.delete_from_db()
    return redirect(url_for("settings.get_settings"))


@settings.route('/settings/item/<item_id>/delete')
@jwt_required(refresh=True)
def delete_item(item_id):
    verify_authentication()
    user = UserModel.find_user_by_item_id(item_id)
    for item in user.items:
        if item['id'] == item_id:
            user_data = user.json()
            user_data['password'] = user.password
            current_app.logger.info("Removing item: %s" % item)
            user_data['items'].remove(item)
            updated_user = UserModel(**user_data)
            updated_user.save_user_to_db()
            return redirect(url_for("settings.get_settings"))


@settings.route('/settings/user/<uid>')
@jwt_required(refresh=True)
def edit_user(uid):
    verify_authentication()
    user = UserModel.find_user_by_uid(uid)
    return render_template('user.html', email=user.email, name=user.name, uid=user.uid)


@settings.route('/settings/user/<uid>/edit', methods=['POST'])
@jwt_required(refresh=True)
def update_user(uid):
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    user = UserModel.find_user_by_email(email)
    if user and uid != user.uid:
        flash('Email address already exists!')
        return redirect(url_for('settings.edit_user', uid=uid))
    edited_user = UserModel.find_user_by_uid(uid)
    edited_user.name = name
    edited_user.email = email
    if password != "":
        edited_user.password = generate_password_hash(password)
    edited_user.save_user_to_db()
    return redirect(url_for("settings.get_settings"))


@settings.route('/settings/item/<item_id>')
@jwt_required(refresh=True)
def edit_item(item_id):
    verify_authentication()
    user = UserModel.find_user_by_item_id(item_id)
    for item in user.items:
        if item['id'] == item_id:
            return render_template('item.html', item_id=item['id'], title=item['title'])


@settings.route('/settings/item/<item_id>/edit', methods=['POST'])
@jwt_required(refresh=True)
def update_item(item_id):
    title = request.form.get('title')
    user = UserModel.find_user_by_item_id(item_id)
    user_data = user.json()
    for num, item in enumerate(user_data['items']):
        if item['id'] == item_id:
            if item['title'] != title:
                user_data['items'][num]['title'] = title
                user_data['password'] = user.password
                updated_user = UserModel(**user_data)
                updated_user.save_user_to_db()
                return redirect(url_for("settings.get_settings"))
