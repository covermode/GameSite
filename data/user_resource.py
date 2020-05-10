from flask_restful import Resource, abort
from flask import jsonify
from . import db_session
from .__all_models import User


def serialize(user):
    return {
        "id": user.id,
        "nickname": user.nickname,
        "badges": [badge.id for badge in user.badges],
        "notes": [note.id for note in user.notes]
    }


class UserResource(Resource):
    @staticmethod
    def get(user_id):
        session = db_session.create_session()

        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            abort(404, message=f"Note not found")

        return jsonify(serialize(user))


class UserListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify([serialize(user) for user in users])
