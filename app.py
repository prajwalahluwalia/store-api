from flask import Flask, request
from db import stores, items
from flask_smorest import abort 
import uuid

app = Flask(__name__)

@app.get('/store')
def get_stores():
    return list(stores.values()), 200

@app.post('/store')
def create_store():
    store_data = request.get_json()
    
    if "name" not in store_data:
        abort(400, message="Store name is required")

    for store in stores.values():
        if store["name"] == store_data["name"]:
            abort(400, message="Store with the same name already exists")

    store_id = uuid.uuid4().hex
    new_store = { **store_data, "id": store_id}
    stores[store_id] = new_store

    return new_store, 201

@app.get('/store/<string:store_id>')
def get_store(store_id):
    try:
        return stores[store_id], 200
    except KeyError:
        abort(404, message="Store not found")

@app.get('/item')
def get_all_items():
    return list(items.values()), 200

@app.post('/item')
def create_item_in_store():
    request_data = request.get_json()
    print(request_data)
    if "store_id" not in request_data or "name" not in request_data or "price" not in request_data:
        abort(400, message="Store ID, name, and price are required to create an item")
    
    if "store_id" in request_data and request_data["store_id"] not in stores:
        abort(404, message="Store not found")

    for item in items.values():
        if item["name"] == request_data["name"] and item["store_id"] == request_data["store_id"]:
            abort(400, message="Item with the same name already exists in the store")

    else:
        item_id = uuid.uuid4().hex
        new_item = { **request_data, "id": item_id}
        items[item_id] = new_item
        return new_item, 201

@app.get('/item/<string:item_id>')
def get_items(name):
    try:
        return items[item_id], 200
    except KeyError:
        abort(404, message="Item not found")