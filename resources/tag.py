import uuid
from flask import Flask, request
from flask_smorest import abort, Blueprint
from flask.views import MethodView
from schemas import TagSchema, StoreSchema, TagItemSchema
from db import db
from models.tag import TagModel
from models.store import StoreModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint("Tags", __name__, description="Operations on tags")

@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            abort(400, message="A tag with the same name already exists in this store.")

        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        
        return tag

@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        db.session.delete(tag)
        db.session.commit()
        return {"message": "Tag deleted."}

@blp.route("/tag")
class TagList(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self):
        return TagModel.query.all()

    @blp.response(202, description="Deletes a tag", example={"message": "Tag deleted."})
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(500, description="Server error.")
    @blp.alt_response(400, description="Returned if Tag is assigned to one or more items. Cannot delete.")
    def delete(self, tag_data):
        tag = TagModel.query.get_or_404(tag_data["id"])
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}

        abort(400, message="Could not delete tag. Make sure tag is not assigned to any items.")


@blp.route("/tag/<string:tag_id>/item/<string:item_id>")
class LinkTagToItem(MethodView):
    @blp.response(200, TagItemSchema)
    def get(self, tag_id, item_id):
        tag = TagModel.query.get_or_404(tag_id)
        item = ItemModel.query.get_or_404(item_id)

        if tag not in item.tags:
            abort(404, message="Tag is not linked to the item.")

        return {"message": "Tag is linked to the item.", "tag": tag, "item": item}

    @blp.response(200, TagItemSchema)
    def post(self, tag_id, item_id):
        tag = TagModel.query.get_or_404(tag_id)
        item = ItemModel.query.get_or_404(item_id)

        if tag in item.tags:
            abort(400, message="Tag is already linked to the item.")

        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {"message": "Tag linked to item successfully.", "tag": tag, "item": item}

    @blp.response(200, TagItemSchema)
    def delete(self, tag_id, item_id):
        tag = TagModel.query.get_or_404(tag_id)
        item = ItemModel.query.get_or_404(item_id)

        if tag not in item.tags:
            abort(404, message="Tag is not linked to the item.")

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {"message": "Tag unlinked from item successfully.", "tag": tag, "item": item}