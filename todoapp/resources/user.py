from uuid import uuid4
from flask_restful import Resource, reqparse
from todoapp.models.user import UserModel
from flask import current_app as app
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt_identity)
from werkzeug.security import generate_password_hash, check_password_hash


class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'title', type=str, required=True, help="Parameter 'title' is not provided"
    )
    parser.add_argument(
        'completed', type=bool, required=True, help="Parameter 'completed' is not provided"
    )
    parser.add_argument(
        'order', type=int, required=True, help="Parameter 'order' is not provided"
    )

    @jwt_required()
    def get(self, item_id):
        user = UserModel.find_user_by_item_id(item_id)
        for item in user['items']:
            if item['id'] == item_id:
                return item
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404

    @jwt_required()
    def delete(self, item_id):
        user = UserModel.find_user_by_item_id(item_id)
        if user:
            for item in user['items']:
                if item['id'] == item_id:
                    user['items'].remove(item)
                    UserModel.update_user_attributes(user['uid'], items=user['items'])
                    return {'message': f"Item '{item_id}' is deleted"}, 204
            else:
                return {'message': f"Item '{item_id}' is not found"}, 404
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404

    @jwt_required()
    def put(self, item_id):
        user = UserModel.find_user_by_item_id(item_id)
        data = Item.parser.parse_args()
        if user:
            for num, item in enumerate(user['items']):
                if item['id'] == item_id:
                    user['items'][num]['title'] = data['title']
                    user['items'][num]['completed'] = data['completed']
                    UserModel.update_user_attributes(user['uid'], items=user['items'])
                    return {'message': f"Item '{item_id}' is updated", 'item': user['items'][num]}, 204
            else:
                return {'message': f"Item '{item_id}' is not found"}, 404
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404


class ItemList(Resource):

    @jwt_required()
    def get(self):
        items = []
        users = UserModel.get_all()
        for user in users:
            items += user['items']
        return items

    @jwt_required()
    def post(self):
        data = Item.parser.parse_args()
        data['id'] = str(uuid4())
        app.logger.info("Got request data from UI: %s" % data)
        uid = get_jwt_identity()
        user = UserModel.find_user_by_uid(uid)
        if user:
            try:
                app.logger.info("Got request data from UI: %s" % data)
                user['items'].append(data)
                UserModel.update_user_attributes(user['uid'], items=user['items'])
            except Exception as e:
                app.logger.debug("An exception occurred: %s" % e)
                return {'message': "An error occurred inserting the item"}, 500
            return data, 201
        else:
            return {'message': f"User '{uid}' is not found"}, 404

    @jwt_required()
    def delete(self):
        users = UserModel.get_all()
        for user in users:
            UserModel.update_user_attributes(user['uid'], items=list())
        return self.get()


class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'email', type=str, required=True, help="Parameter 'email' is not provided"
    )
    parser.add_argument(
        'name', type=str, required=True, help="Parameter 'name' is not provided"
    )
    parser.add_argument(
        'password', type=str, required=True, help="Parameter 'password' is not provided"
    )

    def post(self):
        data = UserRegister.parser.parse_args()
        app.logger.info("Got request data: %s" % data)
        if UserModel.find_user_by_email(data['email']):
            return {"message": "User with this email is already exists"}, 400
        data['password'] = generate_password_hash(data['password'], method='sha256')
        user = UserModel(**data)
        try:
            user.save_user_to_db()
            app.logger.debug("Added user '%s' with email '%s' to DB" % (user.name, user.email))
        except Exception as e:
            app.logger.debug("An exception occurred: %s" % e)
            return {'message': "An error occurred inserting the item"}, 500
        return user.to_dict(), 201


class User(Resource):

    @jwt_required()
    def get(self, uid):
        user = UserModel.find_user_by_uid(uid)
        if not user:
            return {'message': 'User Not Found'}, 404
        return UserModel.hide_password(user), 200

    @jwt_required()
    def delete(self, uid):
        user = UserModel.find_user_by_uid(uid)
        if not user:
            return {'message': 'User Not Found'}, 404
        UserModel(**user).delete_user_from_db()
        return {'message': 'User deleted.'}, 200


class UserLogin(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'email', type=str, required=True, help="Parameter 'email' is not provided"
    )
    parser.add_argument(
        'password', type=str, required=True, help="Parameter 'password' is not provided"
    )

    def post(self):
        data = UserLogin.parser.parse_args()
        user = UserModel.find_user_by_email(data['email'])
        if not user or not check_password_hash(user['password'], data['password']):
            return {'message': 'Invalid credentials'}, 401
        access_token = create_access_token(identity=user['uid'], fresh=True)
        refresh_token = create_refresh_token(user['uid'])
        headers = [('Set-Cookie', f'access_token_cookie={access_token}'),
                   ('Set-Cookie', f'refresh_token_cookie={refresh_token}')]
        return {'login': True, 'access_token': access_token}, 200, headers


class UserItems(Resource):

    @jwt_required(refresh=True)
    def get(self, uid):
        user = UserModel.find_user_by_uid(uid)
        if user:
            return user['items'], 200
        else:
            return {'message': f"User '{uid}' is not found"}, 404

    @jwt_required(refresh=True)
    def post(self, uid):
        user = UserModel.find_user_by_uid(uid)
        if user:
            try:
                data = UserItem.parser.parse_args()
                data['id'] = str(uuid4())
                app.logger.info("Got request data from UI: %s" % data)
                user['items'].append(data)
                app.logger.info("Adding the item to DB: %s" % data)
                UserModel.update_user_attributes(uid, items=user['items'])
            except Exception as e:
                app.logger.debug("An exception occurred: %s" % e)
                return {'message': "An error occurred inserting the item"}, 500
            return data, 201
        else:
            return {'message': f"User '{uid}' is not found"}, 404


class UserItem(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'title', type=str, required=True, help="Parameter 'title' is not provided"
    )
    parser.add_argument(
        'completed', type=bool, required=True, help="Parameter 'completed' is not provided"
    )
    parser.add_argument(
        'order', type=int, required=True, help="Parameter 'order' is not provided"
    )

    @jwt_required()
    def get(self, uid, item_id):
        user = UserModel.find_user_by_uid(uid)
        for item in user['items']:
            if item['id'] == item_id:
                app.logger.info("Got item from DB for user '%s': %s" % (user['name'], item))
                return item, 200
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404

    @jwt_required()
    def delete(self, uid, item_id):
        user = UserModel.find_user_by_uid(uid)
        if user:
            for item in user['items']:
                if item['id'] == item_id:
                    if uid == get_jwt_identity():
                        app.logger.info("Deleting the item from DB: %s" % item)
                        user['items'].remove(item)
                        UserModel.update_user_attributes(uid, items=user['items'])
                        return {'message': f"Item '{item_id}' is deleted"}, 204
                    else:
                        return {'message': "You're not allowed to delete this item"}, 403
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404

    @jwt_required()
    def put(self, uid, item_id):
        data = UserItem.parser.parse_args()
        user = UserModel.find_user_by_uid(uid)
        if user:
            for num, item in enumerate(user['items']):
                if item['id'] == item_id:
                    if uid == get_jwt_identity():
                        app.logger.info("Updating the item: %s" % item)
                        user['items'][num]['title'] = data['title']
                        user['items'][num]['completed'] = data['completed']
                        UserModel.update_user_attributes(uid, items=user['items'])
                        return {'message': f"Item '{item_id}' is updated"}, 204
                    else:
                        return {'message': "You're not allowed to delete this item"}, 403
            else:
                return {'message': f"Item '{item_id}' is not found"}, 404
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404
