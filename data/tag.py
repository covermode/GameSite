import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


association_table = sqlalchemy.Table(
    'note_to_tag', SqlAlchemyBase.metadata,
    sqlalchemy.Column('note', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('note.id')),
    sqlalchemy.Column('tag', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('tag.id'))
)


class Tag(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "tag"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
