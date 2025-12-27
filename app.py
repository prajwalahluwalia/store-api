from flask import Flask, request
from db import stores, items

app = Flask(__name__)

@app.get('/store')
def get_stores():
    return list(stores.values()), 200

@app.post('/store')
def create_store():
    store_data = request.get_json()
    store_id = uuid.uuid4().hex
    new_store = { **store_data, "id": store_id}
    stores[store_id] = new_store

    return new_store, 201

@app.get('/store/<string:store_id>')
def get_store(store_id):
    try:
        return stores[store_id], 200
    except KeyError:
        return {"message": "Store not found"}, 404

@app.get('/items')
def get_all_items():
    return list(items.values()), 200

@app.post('/item')
def create_item_in_store():
    request_data = request.get_json()
    if store_id in request_data:
        item_id = uuid.uuid4().hex
        new_item = { **request_data, "id": item_id}
        items[item_id] = new_item
        return new_item, 201
    else:   
        return {"message": "Store not found"}, 404

@app.get('/item/<string:item_id')
def get_items(name):
    try:
        return items[item_id], 200
    except KeyError:
        return {"message": "Item not found"}, 404