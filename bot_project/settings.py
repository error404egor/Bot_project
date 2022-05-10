import json


with open("forms.json") as forms_file:
    Forms = json.load(forms_file)

Steps_num = 1
# от 0 до 0
All_sex = 1
# 1 - знак того, что пользователь ищет всех
Default_sex = 0
# дефолт
Men_sex = 2

Women_sex = 3

Default_last_watched_id = -1

Server = "127.0.0.1"
Port = 5000