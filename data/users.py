import sqlalchemy
from .db_session import SqlAlchemyBase

from flask_login import UserMixin

from sqlalchemy_serializer import *


class User(SqlAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)

    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    salt_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    icon = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    followers = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    history_watch = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)