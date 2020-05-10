from flask_restful import Resource, abort
from flask import jsonify
from . import db_session
from .__all_models import Note


def serialize(note):
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_date": note.created_date.isoformat(),
        "rating": note.rating,
        "author_id": note.author_id,
        "tags": [tag.id for tag in note.tags]
    }


class NoteResource(Resource):
    @staticmethod
    def get(note_id):
        session = db_session.create_session()
        note = session.query(Note).filter(Note.id == note_id).first()
        if not note:
            abort(404, message=f"Note not found")
        return jsonify(serialize(note))


class NoteListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        notes = session.query(Note).all()
        return jsonify([serialize(note) for note in notes])
