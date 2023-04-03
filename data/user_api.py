import random

import flask
from flask import request, jsonify

from . import db_session
from .video import Video
from .users import User

blueprint = flask.Blueprint(
    'user_api',
    __name__,
    template_folder='templates'
)

@blueprint.route("/api/add_subscribe/<string:user_name>/<string:new_follower>")
def add_subscribe(user_name, new_follower):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == user_name).first()

    if new_follower in str(user.followers).split(" "):
        return "User was followed"

    if len(str(user.followers).split(" ")) == 0 or str(user.followers).split(" ") == [""]:
        user.followers = str(new_follower)
    else:
        print(user.followers)
        user.followers = str(user.followers) + f" {new_follower}"

    user.followers = user.followers.replace("None", "")

    db_sess.commit()

    return "Successfully"

@blueprint.route("/api/delete_subscribe/<string:user_name>/<string:old_follower>")
def delete_subscribe(user_name, old_follower):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == user_name).first()

    if old_follower not in str(user.followers).split(" "):
        return "User not followed"

    all_followers = str(user.followers).split(" ")
    all_followers.remove(old_follower)

    user.followers = " ".join(all_followers)

    print(user.followers)

    db_sess.commit()

    return "Successfully"