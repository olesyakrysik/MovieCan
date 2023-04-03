import sqlalchemy
from .db_session import SqlAlchemyBase

from flask_login import UserMixin

from sqlalchemy_serializer import *


class Video(SqlAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = "videos"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    creator_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    video_filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    preview_filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    url_filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    search_line = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    like = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    count_views = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)

    is_view = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=1)

