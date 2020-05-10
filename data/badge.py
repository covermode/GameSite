import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


associate_table = sqlalchemy.Table(
    'user_to_badge', SqlAlchemyBase.metadata,
    sqlalchemy.Column('user', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('user.id')),
    sqlalchemy.Column('badge', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('badge.id'))
)


class Badge(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "badge"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    icon_src = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True, default="")

    @classmethod
    def generate_myself(cls, icon_src, description):
        inst = cls()
        inst.icon_src = icon_src
        inst.description = description
        return inst

    def __repr__(self):
        return f"<Badge> {self.id} {self.description}"
