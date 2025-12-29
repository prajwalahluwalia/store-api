import uuid
from flask import Flask, request
from flask_smorest import abort, Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from schemas import StoreSchema
from models.store import StoreModel

from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint("Stores", __name__, description="Operations on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required(fresh=True)
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted."}

    # def put(self, store_id):
    #     store = StoreModel.query.get(store_id)
    #     raise NotImplementedError("Put method not implemented yet.")

@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:    
            db.session.add(store)
            db.session.commit()

        except IntegrityError:
            abort(400, message="A store with the same name already exists.")

        except SQLAlchemyError:
            abort(500, message="Error while inserting the store")

        return store