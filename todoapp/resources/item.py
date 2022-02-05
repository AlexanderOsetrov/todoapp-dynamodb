import imp
from flask_restful import Resource, reqparse
from todoapp.models.item import ItemModel
from flask import current_app as app


class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'title', type=str, required=True, help="Parameter 'title' is not provoded"
    )
    parser.add_argument(
        'completed', type=bool, required=True, help="Parameter 'completed' is not provoded"
    )
    parser.add_argument(
        'order', type=int, required=True, help="Parameter 'order' is not provoded"
    )

    def get(self, item_id):
        item = ItemModel.find_by_id(item_id)
        if item:
            app.logger.info("Got the item from DB: %s" % item.json())
            return item.json()
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404        

    def delete(self, item_id):
        item = ItemModel.find_by_id(item_id)
        app.logger.info("Got the item from DB: %s" % item.json())
        if item:
            app.logger.info("Deleting the item from DB: %s" % item.json())
            item.delete_from_db()
            return {'message': f"Item '{item_id}' is deleted"}, 204
        else:
            return {'message': f"Item '{item_id}' is not found"}, 404

    def put(self, item_id):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_id(item_id)
        app.logger.info("Got the item from DB: %s" % item.json())
        item.title = data['title']
        item.completed = data['completed']
        app.logger.info("Updating the item: %s" % item.json())
        item.save_to_db()
        return item.json()


class ItemList(Resource):

    def get(self):
        items = ItemModel.get_all()
        app.logger.info("Got items from DB: %s" % items)
        return items

    def post(self):
        data = Item.parser.parse_args()
        app.logger.info("Got request data from UI: %s" % data)
        item = ItemModel(**data)
        try:
            app.logger.info("Adding the item to DB: %s" % item.json())
            item.save_to_db()
        except Exception:
            return {'message': "An error occured inserting the item"}, 500
        return item.json(), 201

    def delete(self):
        ItemModel.delete_all()
        return self.get()
