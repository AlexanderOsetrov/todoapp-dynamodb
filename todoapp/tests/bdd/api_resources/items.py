from todoapp.tests.bdd.api_resources import base


class Items(base.BaseRequest):

    def get_items(self):
        self.get("/items")
        return self.response_json

    def add_item(self, data):
        self.post("/items", data=data)
        return self.response

    def edit_item(self, item_id, data):
        self.put(f"/items/{item_id}", data)
        return self.response

    def delete_item(self, item_id):
        self.delete(f"/items/{item_id}")
        return self.response
