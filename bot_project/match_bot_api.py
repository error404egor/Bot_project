import sqlalchemy.exc
from flask import Blueprint, jsonify, render_template, request, Response
from data import db_session
from data.user import User
from settings import *
import random
from maps import get_ll_spn


users_blueprint = Blueprint(
    'match_bot_api',
    __name__
)
db_session.global_init("db/users_data.db")


# получение данных пользователя по айди
@users_blueprint.route('/api/get_user_by_id_tg/<int:id_tg>', methods=['GET'])
def get_user_by_tg_id(id_tg):
    session = db_session.create_session()
    try:
        user = session.query(User).filter(User.id_tg == id_tg).one()
    except sqlalchemy.exc.NoResultFound:
        return render_template("no_user_like_that.html"), 400
    return jsonify(
        {
            "id": user.id,
            "id_tg": user.id_tg,
            "chat_id": user.chat_id,
            "username": user.username,
            "name": user.name,
            "sex": user.sex,
            "form_number": user.form_number,
            "form_char": user.form_char,
            "about": user.about,
            "photo": user.photo,
            "address": user.address,
            "searching_sex": user.sex,
            "watched_ids": list(map(int, user.watched_ids.split())),
            "users_liked_ids": list(map(int, user.users_liked_ids.split())),
            "last_watched_id": user.last_watched_id
        }
    )


# отправка нового пользователя в бд
@users_blueprint.route('/api/post_user/<int:id_tg>/<int:chat_id>/<username>', methods=["POST"])
def create_user(id_tg, username, chat_id):
    user = User(id_tg=id_tg, username=username, chat_id=chat_id)
    session = db_session.create_session()
    session.add(user)
    session.commit()
    return Response(status=200)


# отправка данных пользователя на сервер
@users_blueprint.route("/api/post_user_data/", methods=["POST"])
def post_user_data():
    session = db_session.create_session()
    data = request.args
    # получение юзера
    if data.get("id_tg", default=None, type=int) is not None:
        id_tg = data.get("id_tg", default=None, type=int)
        try:
            user = session.query(User).filter(User.id_tg == id_tg).one()
        except sqlalchemy.exc.NoResultFound:
            return render_template("no_user_like_that.html"), 400
    elif data.get("id", default=None, type=int) is not None:
        id_ = data.get("id", default=None, type=int)
        try:
            user = session.query(User).filter(User.id == id_).one()
        except sqlalchemy.exc.NoResultFound:
            return render_template("no_user_like_that.html"), 400
    else:
        return render_template("id_or_id_tg_is_needed.html"), 400

    if data.get("name", default=None, type=str) is not None:
        user.name = data.get("name", default=None, type=str)

    if data.get("sex", default=None, type=int) is not None and \
            data.get("sex", default=None, type=int) in (Men_sex, Women_sex):
        user.sex = data.get("sex", default=None, type=int)

    if data.get("form_number", default=None, type=str) is not None and \
            data.get("form_number", default=None, type=str) in Forms.keys():
        user.form_number = data.get("form_number", default=None, type=int)

    if data.get("form_char", default=None, type=str) is not None and \
            data.get("form_char", default=None, type=str) in Forms[user.form_number]:
        user.form_char = data.get("form_char", default=None, type=str)

    if data.get("about", default=None, type=str) is not None:
        user.about = data.get("about", default=None, type=str)

    if data.get("photo", default=None, type=str) is not None:
        user.photo = data.get("photo", default=None, type=str)

    if data.get("address", default=None, type=str) is not None:
        try:
            get_ll_spn(data.get("address", default=None, type=str))
            user.address = data.get("address", default=None, type=str)
        except ConnectionError:
            pass
        except FileNotFoundError:
            pass

    if data.get("searching_sex", default=None, type=int) is not None \
            and data.get("searching_sex", default=None, type=int) in (All_sex, Men_sex, Women_sex):
        user.searching_sex = data.get("searching_sex", default=None, type=int)

    if data.get("watched_ids", default=None, type=str) is not None:
        try:
            list(map(int, data.get("watched_ids", default=None, type=str).split()))
            user.watched_ids = data.get("watched_ids", default=None, type=str)
        except ValueError:
            pass

    if data.get("users_liked_ids", default=None, type=str) is not None:
        try:
            list(map(int, data.get("users_liked_ids", default=None, type=str).split()))
            user.users_liked_ids = data.get("users_liked_ids", default=None, type=str)
        except ValueError:
            pass

    if data.get("last_watched_id", default=None, type=int) is not None:
        user.last_watched_id = data.get("last_watched_id", default=None, type=int)

    if data.get("username", default=None, type=str) is not None:
        user.username = data.get("username", default=None, type=int)

    if data.get("chat_id", default=None, type=int) is not None:
        user.chat_id = data.get("chat_id", default=None, type=int)

    session.commit()
    return Response(status=200)


# получение пользователя для просмотра данным пользователем
@users_blueprint.route('/api/get_user_to_watch_by_id_tg/<int:id_tg>', methods=['GET'])
def get_user_to_watch_id_tg(id_tg):
    session = db_session.create_session()
    try:
        user = session.query(User).filter(User.id_tg == id_tg).one()
    except sqlalchemy.exc.NoResultFound:
        return render_template("no_user_like_that.html"), 400
    id_tg = session.query(User.id_tg).filter(
        # проверка на заполненную анкету
        ((User.name != "") & (User.searching_sex != 0) & (User.address != "") &
         (User.photo != "") & (User.sex != 0) & (User.form_number != "") &
         (User.form_char != "") & (User.about != "")) &
        # проверка на совпадение скомых полов и полов двух пользователей
        ((User.sex == user.searching_sex) | (user.searching_sex == All_sex)) &
        ((User.searching_sex == user.sex) | (User.searching_sex == All_sex)) &
        # проверка на пользоватей, которые данный пользователь уже посмотрел
        (User.id_tg.not_in(list(map(int, user.watched_ids.split())))) &
        # проверка на одного и того же пользователя
        (User.id_tg != user.id_tg)
        ).all()
    if not id_tg:
        return render_template("no_user_like_that.html"), 400
    return get_user_by_tg_id(random.choice(id_tg)[0])
