import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users_info'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    id_tg = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=True, index=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    sex = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    form_number = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    form_char = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    about = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    photo = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    address = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    searching_sex = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    # 0 - дефолт, 1 - все, 2 - мальчки, 3 - девочки
    watched_ids = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    # строка через пробелы id человек, которых просмотрел полльзователь
    users_liked_ids = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    # строка через пробелы id человек, которые лайкнули пользователя
    last_watched_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=-1)
    # id последнего просматриваемого пользователя
