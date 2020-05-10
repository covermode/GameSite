import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Note(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "note"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    author = orm.relation('User')

    tags = orm.relation("Tag", secondary="note_to_tag", backref="note")

    @classmethod
    def generate_myself(cls, title, content, author_id, tags: list):
        import datetime
        inst = cls()
        inst.title = title
        inst.content = content
        inst.created_date = datetime.datetime.now()
        inst.rating = 0
        inst.author_id = author_id
        for tag in tags:
            inst.tags.append(tag)

        return inst

    def __repr__(self):
        return f"<Note> {self.id} {self.title} by {self.author.nickname}"
