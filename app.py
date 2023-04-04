import hashlib
import os

import flask_login
from flask import Flask, render_template, request, redirect, make_response
from flask_login import login_required, logout_user, login_user

from flask_login import LoginManager

from modules import *

from data.users import User
from data.video import Video
from data import db_session, video_api, user_api

from forms import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "9ECcXCwZGN"
app.config["MAX_CONTENT-PATH"] = 1000000 ** 100

app.register_blueprint(video_api.blueprint)
app.register_blueprint(user_api.blueprint)

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/moviecan.db")

deleteList = []


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        salt = user.salt_password
        password = hashlib.pbkdf2_hmac('sha256', form.password.data.encode('utf-8'), salt, 100000)

        if user and user.salt_password + user.hashed_password == salt + password:
            login_user(user, remember=form.remember_me.data)
            print("login")
            return redirect("/")

        return render_template("login.html", message="Неправильный логин или пароль",
                               form=form)

    params = dict()
    params["title"] = "Авторизация"
    return render_template("login.html", **params, form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit() and request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        avatar = request.files["input_avatar"]
        avatar_type = avatar.filename.split(".")[-1]

        if not avatar:
            params = dict()
            params["title"] = "Регистрация"
            return render_template("register.html", **params, form=form, message="Выберите аватарку")

        elif not user:
            salt = os.urandom(32)
            password = hashlib.pbkdf2_hmac('sha256', form.password.data.encode('utf-8'), salt, 100000)

            avatar_filename = generate_name("static/icons") + "." + avatar_type

            with open(f"static/icons/{avatar_filename}", mode="wb") as avatar_file:
                avatar_file.write(avatar.read())

            user = User()
            user.name = form.name.data
            user.icon = avatar_filename
            user.age = form.age.data
            user.email = form.email.data
            user.hashed_password = password
            user.salt_password = salt
            db_sess.add(user)
            db_sess.commit()

            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        else:
            return render_template("register.html", message="Такой пользователь уже существует",
                                   form=form)

    params = dict()
    params["title"] = "Регистрация"
    return render_template("register.html", **params, form=form)


@app.route("/")
def index():
    params = dict()
    params["title"] = "Главная страница"
    return render_template("index.html", **params)


@app.route("/watch")
def watch():
    db_sess = db_session.create_session()

    args = request.args.to_dict()
    v = args.get("v")

    video = db_sess.query(Video).filter(Video.url_filename == v).first()
    video.count_views += 1

    creator_id = db_sess.query(Video).filter(Video.url_filename == v).first().creator_id
    creator = db_sess.query(User).filter(User.id == creator_id).first()

    params = dict()
    params["title"] = video.name
    params["menu"] = [{"name": "Закладки", "url": "#"}, {"name": "О нас", "url": "#"}]
    params["url_filename"] = video.url_filename
    params["video_filename"] = video.video_filename
    params["preview_filename"] = video.preview_filename
    params["icon"] = creator.icon if (creator.icon != "" and creator.icon is not None) else "default.png"
    params["creator_name"] = creator.name
    params["channel_id"] = creator.id

    followers_count = len(str(creator.followers).split(" ")) if (
            creator.followers != "" and creator.followers is not None) else 0
    count_like = len(str(video.like).split(" ")) if (video.like != "" and video.like is not None) else 0
    count_views = video.count_views

    params["channel_url"] = f"/channel/{db_sess.query(User).get(video.creator_id).name}"
    params["followers_count"] = str(followers_count) + " " + word_declension(followers_count,
                                                                             "подписчик,подписчика,подписчиков")

    params["video_name"] = video.name
    params["video_id"] = video.id
    params["description"] = find_link_in_text(video.description)
    params["count_like"] = str(count_like)
    params["count_views"] = str(count_views) + " " + word_declension(count_views, "просмотр,просмотра,просмотров")

    try:
        params["current_user_id"] = flask_login.current_user.id

    except Exception:
        params["current_user_id"] = -1

    resp = make_response(render_template("watch.html", **params))

    try:
        resp.set_cookie("video_id", str(video.id),
                        max_age=60 * 60 * 24 * 365 * 2)

        resp.set_cookie("is_like", str(str(flask_login.current_user.id) in str(
            db_sess.query(Video).filter(Video.url_filename == video.url_filename).first().like).split(" ")),
                        max_age=60 * 60 * 24 * 365 * 2)

    except Exception:
        resp.set_cookie("video_id", "0",
                        max_age=60 * 60 * 24 * 365 * 2)

        resp.set_cookie("is_like", str(False), max_age=60 * 60 * 24 * 365 * 2)

    resp.set_cookie("current_user_id", str(params["current_user_id"]),
                    max_age=60 * 60 * 24 * 365 * 2)

    resp.set_cookie("is_follower", str(str(params["current_user_id"]) in str(creator.followers).split(" ")),
                    max_age=60 * 60 * 24 * 365 * 2)

    db_sess.commit()

    return resp


@app.route("/create_video", methods=["GET", "POST"])
@login_required
def create_video():
    form = CreateVideoForm()

    if form.validate_on_submit() and request.method == "POST":
        preview = request.files["input_preview"]
        video = request.files["input_video"]

        if not preview or not video:
            params = dict()
            params["title"] = "Созднание Видеоролика"
            return render_template("create_video.html", **params, form=form, message="Выберите превью или видео")

        else:
            url_filename = generate_name("static/preview")
            video_filename = url_filename + "." + video.filename.split(".")[-1]
            preview_filename = url_filename + "." + preview.filename.split(".")[-1]

            with open(f"static/preview/{preview_filename}", mode="wb") as preview_file:
                preview_file.write(preview.read())

            with open(f"static/video/{video_filename}", mode="wb") as video_file:
                video_file.write(video.read())

            db_sess = db_session.create_session()
            video = Video()
            video.video_filename = video_filename
            video.preview_filename = preview_filename
            video.url_filename = url_filename
            video.creator_id = flask_login.current_user.id
            video.creator_name = flask_login.current_user.name
            video.name = form.name.data.strip()
            video.description = form.description.data.strip()
            video.search_line = video.name.lower() + " " + video.description.lower()
            video.is_view = 1

            db_sess.add(video)
            db_sess.commit()

        return redirect("/")

    params = dict()
    params["title"] = "Созднание Видеоролика"
    return render_template("create_video.html", **params, form=form)


@app.route("/delete_video/<string:url_filename>")
@login_required
def delete_video(url_filename):
    global deleteList

    db_sess = db_session.create_session()

    video = db_sess.query(Video).filter(Video.url_filename == url_filename).first()

    if video:
        video_filename = video.video_filename
        preview_filename = video.preview_filename

        deleteList.append([video_filename, preview_filename])

        db_sess.delete(video)
        db_sess.commit()
        db_sess.close()

    else:
        return 404

    return redirect("/")


@app.route("/edit_video/<string:url_filename>", methods=["GET", "POST"])
@login_required
def edit_video(url_filename):
    form = VideoEditForm()
    params = dict()
    params["title"] = "Редактирование видео"

    print(5)

    if request.method == "GET":
        db_sess = db_session.create_session()
        video = db_sess.query(Video).filter(Video.url_filename == url_filename).first()

        if video:
            form.name.data = video.name
            form.description.data = video.description

            params["preview_filename"] = video.preview_filename

        else:
            return 404

    if form.validate_on_submit() and request.method == "POST":
        db_sess = db_session.create_session()
        video = db_sess.query(Video).filter(Video.url_filename == url_filename).first()

        if video:
            video.name = form.name.data
            video.description = form.description.data
            video.search_line = video.name.lower() + " " + video.description.lower()

            db_sess.commit()

            return redirect("/")

        else:
            return 404

    return render_template("edit_video.html", **params, form=form)


@app.route("/channel/<string:channel>")
def channel(channel):
    db_sess = db_session.create_session()

    creator_channel = db_sess.query(User).filter(User.name == channel).first()
    followers_count = len(str(creator_channel.followers).split(" ")) if (
            creator_channel.followers is not None and creator_channel.followers != "") else 0

    params = dict()
    params["title"] = f"Канал {channel}"
    params["channel_icon"] = creator_channel.icon
    params["channel_name"] = creator_channel.name
    params["channel_id"] = creator_channel.id
    params["channel_followers"] = str(followers_count) + " " + word_declension(followers_count,
                                                                               "подписчик,подписчика,подписчиков")

    try:
        params["current_user_id"] = flask_login.current_user.id

    except Exception:
        params["current_user_id"] = -1

    resp = make_response(render_template("channel.html", **params))

    try:
        resp.set_cookie("is_follower",
                        str(str(flask_login.current_user.id) in str(creator_channel.followers).split(" ")),
                        max_age=60 * 60 * 24 * 365 * 2)

        resp.set_cookie("current_user_id", str(flask_login.current_user.id),
                        max_age=60 * 60 * 24 * 365 * 2)


    except Exception:
        resp.set_cookie("is_follower", str(False),
                        max_age=60 * 60 * 24 * 365 * 2)

        resp.set_cookie("current_user_id", "-1",
                        max_age=60 * 60 * 24 * 365 * 2)

    return resp


@app.route("/edit_channel/<int:id_channel>", methods=["GET", "POST"])
@login_required
def edit_channel(id_channel):
    form = ChannelEditForm()
    params = dict()
    params["title"] = "Редактирование канала"

    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id_channel).first()

        if user:
            form.name.data = user.name
            form.age.data = user.age
            form.email.data = user.email

            params["icon"] = user.icon

        else:
            return 404

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id_channel).first()

        avatar = request.files["input_avatar"]
        avatar_type = avatar.filename.split(".")[-1]

        if user:
            avatar_filename = generate_name("static/icons") + "." + avatar_type

            with open(f"static/icons/{avatar_filename}", mode="wb") as avatar_file:
                avatar_file.write(avatar.read())

            user.name = form.name.data
            user.age = form.age.data
            user.email = form.email.data
            user.icon = avatar_filename

            db_sess.commit()

            return redirect("/")

        else:
            return 404

    print(form.validate_on_submit())

    if not "icon" in params.keys():
        params["icon"] = "default.png"

    return render_template("edit_channel.html", **params, form=form)


@app.route("/shorts")
def shorts():
    params = dict()
    params["title"] = "Короткие видео пока-что отвсутствуют"
    return render_template("shorts.html", **params)


@app.errorhandler(404)
def not_found(_):
    return "Страница не найдена"


@app.errorhandler(401)
def not_found(_):
    return "Вы не авторизовались"


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000)
