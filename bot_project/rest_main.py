import match_bot_api
from flask import Flask
from settings import Port, Server

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

if __name__ == '__main__':
    print("a")
    app.register_blueprint(match_bot_api.users_blueprint)
    print("b")
    app.run(Server, Port)
