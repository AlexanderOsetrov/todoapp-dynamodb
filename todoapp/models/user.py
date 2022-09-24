from uuid import uuid4
from botocore.exceptions import ClientError
from todoapp.dynamo import create_or_get_table
from boto3.dynamodb.conditions import Attr
from flask import current_app as app
from werkzeug.security import generate_password_hash
from typing import List
from copy import deepcopy


class UserModel:

    table = create_or_get_table()

    def __init__(self, email, name, password, uid=None, items=None):
        self.email = email
        self.name = name
        self.password = password
        self.uid = str(uuid4()) if uid is None else uid
        self.items = [] if items is None else items

    @property
    def formatted_items(self):
        for item in self.items:
            item['order'] = int(item['order'])
        return self.items

    def save_user_to_db(self):
        self.table.put_item(
            Item={
                'uid': self.uid,
                'email': self.email,
                'name': self.name,
                'password': self.password,
                'items': self.items}
        )

    def delete_user_from_db(self):
        self.table.delete_item(Key={'uid': self.uid})

    @staticmethod
    def _hide_password(response):
        _response = deepcopy(response)
        try:
            if isinstance(_response, list):
                for item in _response:
                    item.pop('password')
            elif isinstance(_response, dict):
                _response.pop('password')
            return _response
        except KeyError:
            return _response

    @staticmethod
    def _format_items(items):
        for item in items:
            item['order'] = int(item['order'])
        return items

    @staticmethod
    def get_update_parameters(request_body):
        execution_list = []
        attribute_names = dict()
        attribute_values = dict()
        for key, value in request_body.items():
            execution_list.append(f"#{key} = :{key}")
            attribute_names[f"#{key}"] = key
            attribute_values[f":{key}"] = value
        update_expression = f"SET {', '.join(execution_list)}"
        return update_expression, attribute_names, attribute_values

    @classmethod
    def get_by_key(cls, key, value):
        response = cls.table.get_item(
            Key={key: value}
        )
        try:
            app.logger.debug("Found record by key '%s' equals '%s':\n%s" % (
                key, value, cls._hide_password(response['Item'])))
            response["Item"]["items"] = cls._format_items(response["Item"]["items"])
            return response["Item"]
        except LookupError:
            return {}

    @classmethod
    def get_by_attribute_equal(cls, attribute, value):
        response = cls.table.scan(
            FilterExpression=Attr(attribute).eq(value)
        )
        app.logger.debug(
            "Found record by attribute '%s' equals to '%s':\n%s" % (
                attribute, value, cls._hide_password(response)))
        try:
            if len(response['Items']) > 1:
                return response['Items']
            else:
                return response['Items'][0]
        except LookupError:
            return {}

    @classmethod
    def get_by_attribute_contains(cls, attribute, value):
        response = cls.table.scan(
            FilterExpression=Attr(attribute).contains(value)
        )
        app.logger.debug(
            "Found data by attribute '%s' containing '%s':\n%s" % (
                attribute, value, cls._hide_password(response)))
        try:
            if len(response['Items']) > 1:
                return response['Items']
            else:
                return response['Items'][0]
        except LookupError:
            return {}

    @classmethod
    def find_user_by_uid(cls, uid):
        return cls.get_by_key("uid", uid)

    @classmethod
    def find_user_by_name(cls, name):
        return cls.get_by_attribute_equal("name", name)

    @classmethod
    def find_user_by_email(cls, email):
        return cls.get_by_attribute_equal("email", email)

    @classmethod
    def find_user_by_item_id(cls, item_id):
        users = cls.get_all()
        for user in users:
            for item in user['items']:
                if item['id'] == item_id:
                    app.logger.debug("User with item %s found:\n%s" % (
                        item_id, cls._hide_password(user)))
                    return user
        else:
            app.logger.debug("User with item '%s' not found" % item_id)
            return {}

    @classmethod
    def get_all(cls):
        response = cls.table.scan()['Items']
        app.logger.debug("Records found:\n%s" % cls._hide_password(response))
        return response

    @classmethod
    def delete_all(cls):
        for item in cls.table.scan()['Items']:
            cls.table.delete_item(Key={'uid': item.get('uid')})

    @classmethod
    def update_user_attributes(cls, uid: str, name: str = None, email: str = None,
                               password: str = None, items: List = None):
        update_parameters = {}
        if name is not None:
            update_parameters['name'] = name
        if email is not None:
            update_parameters['email'] = email
        if password is not None:
            update_parameters['password'] = generate_password_hash(password)
        if items is not None:
            update_parameters['items'] = items
        try:
            expression, update_names, update_values = cls.get_update_parameters(update_parameters)
            response = cls.table.update_item(
                Key={'uid': uid},
                UpdateExpression=expression,
                ExpressionAttributeNames=dict(update_names),
                ExpressionAttributeValues=dict(update_values))
            return response
        except ClientError as e:
            app.logger.error(
                "Couldn't update data in table '%s' due to %s: %s" % (
                    cls.table.name,
                    e.response['Error']['Code'],
                    e.response['Error']['Message']
                )
            )
            raise
