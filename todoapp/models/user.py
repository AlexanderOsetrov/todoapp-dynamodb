from uuid import uuid4
from todoapp.dynamo import create_or_get_table
from boto3.dynamodb.conditions import Attr
from flask import current_app as app


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

    def json(self):
        return {'uid': self.uid, 'email': self.email, 'name': self.name, 'items': self.formatted_items}

    @staticmethod
    def db_item_to_object(db_item):
        return UserModel(
            email=db_item['email'],
            name=db_item['name'],
            uid=db_item['uid'],
            items=db_item['items'],
            password=db_item['password'])

    @classmethod
    def get_by_attribute_equal(cls, attribute, value):
        data = cls.table.scan(
            FilterExpression=Attr(attribute).eq(value)
        )
        app.logger.debug("Found data by attribute %s equals to %s:\n%s" % (attribute, value, data))
        try:
            return data['Items'][-1]
        except LookupError:
            return {}

    @classmethod
    def get_by_attribute_contains(cls, attribute, value):
        data = cls.table.scan(
            FilterExpression=Attr(attribute).contains(value)
        )
        app.logger.debug("Found data by attribute %s containing %s:\n%s" % (attribute, value, data))
        try:
            return data['Items'][-1]
        except LookupError:
            return {}

    @classmethod
    def find_user_by_uid(cls, uid):
        user = cls.table.get_item(Key={'uid': uid})
        app.logger.debug("Found user by key uid equals %s:\n%s" % (uid, user))
        if user:
            return cls.db_item_to_object(user['Item'])
        else:
            return {}

    @classmethod
    def find_user_by_name(cls, name):
        user = cls.get_by_attribute_equal("name", name)
        try:
            return cls.db_item_to_object(user)
        except LookupError:
            return {}

    @classmethod
    def find_user_by_email(cls, email):
        user = cls.get_by_attribute_equal("email", email)
        try:
            return cls.db_item_to_object(user)
        except LookupError:
            return {}

    @classmethod
    def find_user_by_item_id(cls, item_id):
        users = cls.get_all()
        for user in users:
            for item in user.items:
                if item['id'] == item_id:
                    app.logger.debug("User with item %s found:\n%s" % (item_id, user.json()))
                    return user
        else:
            app.logger.debug("User with item %s not found" % item_id)
            return {}

    def save_user_to_db(self):
        self.table.put_item(
            Item={
                'uid': self.uid,
                'email': self.email,
                'name': self.name,
                'password': self.password,
                'items': self.items}
        )

    def delete_from_db(self):
        self.table.delete_item(
            Key={'uid': self.uid}
        )

    @classmethod
    def get_all(cls):
        users = cls.table.scan()['Items']
        app.logger.debug("Users found:\n%s" % users)
        return [UserModel.db_item_to_object(user) for user in users]

    @classmethod
    def delete_all(cls):
        for item in cls.table.scan()['Items']:
            cls.table.delete_item(Key={'uid': item.get('uid')})
