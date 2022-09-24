from todoapp.models.user import UserModel
from flask_jwt_extended import jwt_required
from flask import Blueprint, render_template, redirect, url_for, current_app, request
from todoapp.app_setup import verify_authentication


item = Blueprint('item', __name__)


@item.route('/item/<item_id>/delete')
@jwt_required(refresh=True)
def delete_item(item_id):
    verify_authentication()
    user = UserModel.find_user_by_item_id(item_id)
    for _item in user['items']:
        if _item['id'] == item_id:
            current_app.logger.info("Removing item: %s" % _item)
            user['items'].remove(_item)
            UserModel.update_user_attributes(user['uid'], items=user['items'])
            return redirect(url_for("settings.get_settings"))


@item.route('/item/<item_id>')
@jwt_required(refresh=True)
def edit_item(item_id):
    verify_authentication()
    user = UserModel.find_user_by_item_id(item_id)
    for _item in user['items']:
        if _item['id'] == item_id:
            return render_template('item.html', item_id=_item['id'], title=_item['title'])


@item.route('/item/<item_id>/edit', methods=['POST'])
@jwt_required(refresh=True)
def update_item(item_id):
    title = request.form.get('title')
    user = UserModel.find_user_by_item_id(item_id)
    for num, _item in enumerate(user['items']):
        if _item['id'] == item_id:
            if _item['title'] != title:
                user['items'][num]['title'] = title
                UserModel.update_user_attributes(user['uid'], items=user['items'])
                return redirect(url_for("settings.get_settings"))
