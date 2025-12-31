import uuid

from flask_smorest import abort, Blueprint
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256

from models.user import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST
from flask_jwt_extended import jwt_required, get_jwt, create_access_token, create_refresh_token, get_jwt_identity

from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


blp = Blueprint("Users", "users", description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        print(user_data)
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(400, message="A user with that username already exists.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )

        try:
            db.session.add(user)
            db.session.commit()

        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the user.")

        return {"message": "User created successfully."}, 201

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=str(user.id), fresh=True)
            refresh_token = create_refresh_token(identity=str(user.id))

            return {"message": "Login successful.", "access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Invalid credentials.")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "User logged out successfully."}, 200

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}

    @blp.arguments(UserSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        user = UserModel.query.get(user_id)
        check_user = UserModel.query.filter(UserModel.username == user_data["username"]).first()
        
        if check_user and check_user.id != user_id:
            abort(400, message="A user with that username already exists.")

        if user:
            user.username = user_data["username"]
            user.password = pbkdf2_sha256.hash(user_data["password"])

        else:
            user = UserModel(
                id=user_id,
                username=user_data["username"],
                password=pbkdf2_sha256.hash(user_data["password"])
            )

        db.session.add(user)
        db.session.commit()

        return user

@blp.route("/users")
class UserList(MethodView):
    @blp.response(200, UserSchema(many=True))
    def get(self):
        return UserModel.query.all()

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt()["sub"]
        new_token = create_access_token(identity=current_user, fresh=False)
        # to create one non fresh token
        # jti = get_jwt()["jti"]
        # BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200