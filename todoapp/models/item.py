from uuid import uuid4
from todoapp.dynamo import create_or_get_table


class ItemModel:

    table = create_or_get_table()

    def __init__(self, title, completed, order, item_id=None):
        self.title = title
        self.completed = completed
        self.order = order
        if item_id is None:
            self.id = str(uuid4())
        else:
            self.id = item_id

    def json(self):
        return {'id': self.id, 'title': self.title, 'completed': self.completed, 'order': int(self.order)}

    @staticmethod
    def db_item_to_object(db_item):
        return ItemModel(
            title=db_item['title'],
            completed=db_item['completed'],
            order=int(db_item['order']),
            item_id=db_item['id'])

    @classmethod
    def find_by_id(cls, item_id):
        item = cls.table.get_item(Key={'id': item_id})
        if item:
            return cls.db_item_to_object(item['Item'])
        else:
            return {}

    def save_to_db(self):
        self.table.put_item(
            Item={'id': self.id, 'title': self.title, 'completed': self.completed, 'order': self.order}
        )

    def delete_from_db(self):
        self.table.delete_item(
            Key={'id': self.id}
        )

    @classmethod
    def get_all(cls):
        items = cls.table.scan()['Items']
        for item in items:
            item['order'] = int(item['order'])
        return sorted(items,  key=lambda k: k['order'])

    @classmethod
    def delete_all(cls):
        for item in cls.table.scan()['Items']:
            cls.table.delete_item(Key={'id': item.get('id')})
