import os
import random

import flask
from flask import request, jsonify

from . import db_session
from .video import Video
from .users import User

blueprint = flask.Blueprint(
    'video_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/video/<string:search_query>/<int:count>')
def get_video(search_query, count):
    db_sess = db_session.create_session()

    if str(search_query) == "null" or search_query is None:
        search_query = ""

    video = db_sess.query(Video).filter(Video.search_line.like("%" + search_query + "%")).all()
    random.shuffle(video)

    if video:
        content = []

        for v in video[:count]:
            creator = db_sess.query(User).filter(User.id == v.creator_id).first()

            v = v.to_dict(only=("creator_id", "video_filename", "preview_filename", "url_filename", "name", "description", "count_views", "is_view"))
            v.update({"channel_icon": creator.icon if (creator.icon != "" and creator.icon is not None) else "default"})
            v.update({"name": v["name"] if len(v["name"]) < 25 else v["name"][:22] + "..."})
            v.update({"creator_name": creator.name})

            content.append(v)

        if content:
            return jsonify(
                {
                    "content": content
                }
            )

    else:
        return jsonify(
            {
                "content": []
            }
        )

@blueprint.route('/api/video/add_like/<int:video_id>/<int:user_id>')
def add_like(video_id, user_id):
    db_sess = db_session.create_session()

    video = db_sess.query(Video).filter(Video.id == video_id).first()

    if str(user_id) in str(video.like).split(" "):
        return "User was liked"

    if len(str(video.like).split(" ")) == 0 or str(video.like).split(" ") == [""]:
        video.like = str(user_id)
    else:
        print(str(video.like).split(" "))
        video.like = str(video.like) + f" {user_id}"

    db_sess.commit()

    video.like = video.like.replace("None", "")

    return "Successfully"


@blueprint.route('/api/video/delete_like/<int:video_id>/<int:user_id>')
def delete_like(video_id, user_id):
    db_sess = db_session.create_session()
    video = db_sess.query(Video).filter(Video.id == video_id).first()

    if str(user_id) not in str(video.like).split(", "):
        return "User not like"

    all_likes = str(video.like).split(", ")
    all_likes.remove(str(user_id))
    video.like = ", ".join(all_likes)

    db_sess.commit()

    return "Successfully"

