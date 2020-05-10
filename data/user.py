import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'user'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    ava = sqlalchemy.Column(sqlalchemy.String, nullable=True, default="")
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime)

    badges = orm.relation("Badge", secondary="user_to_badge", backref="badge")
    notes = orm.relation("Note", back_populates="author")

    @classmethod
    def generate_myself(cls, surname, name, nickname, age, email,
                        password):
        import datetime

        inst = cls()
        inst.surname = surname
        inst.name = name
        inst.nickname = nickname
        inst.age = age
        inst.email = email
        inst.set_password(password)
        inst.modified_date = datetime.datetime.now()
        return inst

    def __repr__(self):
        return f"<User> {self.id} {self.name} {self.surname} {self.nickname}"

    def set_password(self, pw):
        self.hashed_password = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.hashed_password, pw)
