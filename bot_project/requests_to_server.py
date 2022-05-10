from settings import Server, Port
import requests

url = f"http://{Server}:{Port}"


def is_registred(id_tg):
    request = requests.get(f"{url}/api/get_user_by_id_tg/{id_tg}")
    print(request)
    return bool(request)


def add_user(id_tg, chat_id, username):
    request = requests.post(f"{url}/api/post_user/{id_tg}/{chat_id}/{username}")
    return bool(request)


def get_user_data(id_tg):
    request = requests.get(f"{url}/api/get_user_by_id_tg/{id_tg}")
    if not request:
        return {}
    data = request.json()
    return data


def post_user_data(**kwargs):
    if "users_liked_ids" in kwargs.keys():
        kwargs["users_liked_ids"] = " ".join(list(map(str, kwargs["users_liked_ids"])))
    if "watched_ids" in kwargs.keys():
        kwargs["watched_ids"] = " ".join(list(map(str, kwargs["watched_ids"])))
    print(kwargs)
    request = requests.post(f"{url}/api/post_user_data/", params=kwargs)
    return bool(request)


def get_user_to_watch(id_tg):
    request = requests.get(f"{url}/api/get_user_to_watch_by_id_tg/{id_tg}")
    if not request:
        return {}
    data = request.json()
    return data
