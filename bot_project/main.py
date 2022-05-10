import logging
import telegram.update
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CommandHandler
from keyboards import *
from settings import *
from requests_to_server import *
from maps import get_ll_spn, get_address_photo
import base64
import io

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5347697668:AAH6z32nKSc8cWQ4si6s7axLk_WfHuNtKvg'


# ----------------------------------------------- главное меню ---------------------------------------------------------


def start(update, context: telegram.ext.callbackcontext.CallbackContext):
    update.message.reply_text(
        "Категорически приветствую! "
        "Вы в меню.",
        reply_markup=main_keyboard)


def my_profile(update, context):
    user = get_user_data(update.message.from_user.id)
    if not user:
        update.message.reply_text(
            f"Её нету.",
            reply_markup=main_keyboard
        )
        return ConversationHandler.END
    # проверка на целостность данных
    if (not user["name"] or
            not user["sex"] or
            not user["photo"] or
            not user["form_number"] or
            not user["form_char"] or
            not user["address"] or
            not user["searching_sex"] or
            not user["about"]):
        update.message.reply_text(
            f"Вы не до конца заполнили анкету. Дозаполните ее нажав на {CHANGE_PROFILE}.",
            reply_markup=main_keyboard
        )
        return ConversationHandler.END
    update.message.reply_text(
        "Вот твоя анкета:\n",
        reply_markup=main_keyboard)
    send_form(update, context, user["id_tg"])


def entery_menu(update, context):
    update.message.reply_text(
        "Вы в меню.",
        reply_markup=main_keyboard)
    return ConversationHandler.END


# ---------------------------------------------- заполнение профиля ----------------------------------------------------


def bad_input(update):
    update.message.reply_text(
        "Упс! Вы ввели что-то неправильно! Повторите ввод."
    )


def bad_sever_connection(update):
    update.message.reply_text(
        "Наблюдаются неполадки с сервером бота. Повторите попытку позднее."
    )


def ask_name(update: telegram.update.Update, context):
    if not is_registred(update.message.from_user.id):
        if not  update.message.from_user.username:
            update.message.reply_text(
                "У вас нету краткого имени. Сделайте его в настройках телеграма."
            )
            return ConversationHandler.END
        done = add_user(update.message.from_user.id, update.message.chat_id, update.message.from_user.username)
        if not done:
            bad_sever_connection(update)
            return ConversationHandler.END

    data = get_user_data(update.message.from_user.id)
    if not data:
        bad_sever_connection(update)
        return ConversationHandler.END

    context.user_data["name"] = data["name"]
    context.user_data["sex"] = data["sex"]
    context.user_data["form_number"] = data["form_number"]
    context.user_data["form_char"] = data["form_char"]
    context.user_data["about"] = data["about"]
    context.user_data["photo"] = data["photo"]
    context.user_data["address"] = data["address"]
    context.user_data["searching_sex"] = data["searching_sex"]
    update.message.reply_text(
        "Как тебя зовут?",
        reply_markup=get_name_choose_keyboard() if not context.user_data["name"]
        else get_name_choose_keyboard(context.user_data["name"])
    )
    return 0


def ask_sex(update, context):
    context.user_data["name"] = update.message.text
    done = post_user_data(id_tg=update.message.from_user.id, name=context.user_data["name"])
    if not done:
        bad_sever_connection(update)
        return 0
    update.message.reply_text(
        f"Отлично, {context.user_data['name']}! Теперь выбери свой пол.",
        reply_markup=choose_sex_keyboard
    )
    return 1


def ask_form_number(update, context):
    if update.message.text in (MEN, WOMEN):
        context.user_data["sex"] = 2 if update.message.text == MEN else 3
        done = post_user_data(id_tg=update.message.from_user.id, sex=context.user_data["sex"])
        if not done:
            bad_sever_connection(update)
            return 1
        update.message.reply_text(
            "Хорошо, теперь определимся с вашим классом. Для начала укажите номер класса.",
            reply_markup=choose_form_number_keyboard
        )
        return 2
    else:
        bad_input(update)
        return 1


def ask_form_letter(update, context):
    if update.message.text in Forms.keys():
        context.user_data["form_number"] = update.message.text
        done = post_user_data(id_tg=update.message.from_user.id, form_number=context.user_data["form_number"])
        if not done:
            bad_sever_connection(update)
            return 2
        update.message.reply_text(
            "Теперь напиши букву класса",
            reply_markup=get_choose_form_letter_keyboard(context.user_data["form_number"])
        )
        return 3
    else:
        bad_input(update)
        return 2


def ask_for_introduction(update, context):
    if update.message.text in Forms[context.user_data["form_number"]]:
        context.user_data["form_char"] = update.message.text
        done = post_user_data(id_tg=update.message.from_user.id, form_char=context.user_data["form_char"])
        if not done:
            bad_sever_connection(update)
            return 3
        update.message.reply_text(
            "Теперь напиши немного о себе.",
            reply_markup=get_choose_text_keyboard(already_has_text=True if context.user_data["about"] else False)
        )
        return 4
    else:
        bad_input(update)
        return 3


def ask_for_photo(update, context):
    if update.message.text != CHOOSE_PREVIOUST_TEXT:
        context.user_data["about"] = update.message.text
    done = post_user_data(id_tg=update.message.from_user.id, about=context.user_data["about"])
    if not done:
        bad_sever_connection(update)
        return 4
    update.message.reply_text(
        "Пришлите своё фото.",
        reply_markup=get_choose_photo_keyboard(already_has_photo=True if context.user_data["photo"] else False)
    )
    return 5


def ask_for_address(update: telegram.update.Update, context):
    if update.message.photo:
        file = update.message.photo[-1].get_file()
        photo = io.BytesIO()
        file.download(out=photo)
        photo.seek(0)
        context.user_data["photo"] = base64.b64encode(photo.read())
        context.bot.send_photo(update.message.chat_id, base64.b64decode(context.user_data["photo"]))
        done = post_user_data(id_tg=update.message.from_user.id, photo=context.user_data["photo"])
        if not done:
            bad_sever_connection(update)
            return 5
        keyboard = get_choose_address_keyboard(
            preaddress=context.user_data["address"] if context.user_data["address"] else "")
        update.message.reply_text("Теперь напишите ваш адрес.",
                                  reply_markup=keyboard)
        return 6
    elif update.message.text == CHOOSE_PREVIOUST_PHOTO and context.user_data["photo"]:
        context.bot.send_photo(update.message.chat_id, base64.b64decode(context.user_data["photo"]))
        keyboard = get_choose_address_keyboard(
            preaddress=context.user_data["address"] if context.user_data["address"] else "")
        update.message.reply_text("Теперь напишите ваш адрес.",
                                  reply_markup=keyboard)
        return 6
    else:
        bad_input(update)
        return 5


def ask_searching_sex(update, context):
    address = update.message.text
    try:
        ll, spn = get_ll_spn(address)
        context.user_data["address"] = address
        photo = get_address_photo(ll, spn)
        context.bot.send_photo(update.message.chat_id, photo)
        context.user_data["address"] = address
        done = post_user_data(id_tg=update.message.from_user.id, address=context.user_data["address"])
        if not done:
            bad_sever_connection(update)
            return 6
        update.message.reply_text(
            "Кого ты ищешь?",
            reply_markup=choose_searching_sex_keyboard
        )
        return 7
    except ConnectionError:
        keyboard = get_choose_address_keyboard(
            preaddress=context.user_data["address"] if context.user_data["address"] else "")
        update.message.reply_text(
            "Упс, соединение с картами сейчас плохое, вернитесь к заполнению позже.",
            reply_markup=keyboard
        )
        return 6
    except FileNotFoundError:
        keyboard = get_choose_address_keyboard(
            preaddress=context.user_data["address"] if context.user_data["address"] else "")
        update.message.reply_text(
            "Не удалось найти такого места(",
            reply_markup=keyboard
        )
        return 6


def end_registration(update, context):
    if update.message.text in (MEN_SEARCHING, WOMEN_SEARCHING, ALL):
        if update.message.text == MEN_SEARCHING:
            context.user_data["searching_sex"] = 2
        elif update.message.text == WOMEN_SEARCHING:
            context.user_data["searching_sex"] = 3
        else:
            context.user_data["searching_sex"] = 1
        done = post_user_data(id_tg=update.message.from_user.id, searching_sex=context.user_data["searching_sex"])
        if not done:
            bad_sever_connection(update)
            return 7
        update.message.reply_text(
            "Регистрация завершена!",
            reply_markup=main_keyboard
        )
        return ConversationHandler.END
    else:
        bad_input(update)
        return 7


edit_conv_handler = ConversationHandler(
    # Точка входа в диалог.
    # В данном случае — команда /start. Она задаёт первый вопрос.
    entry_points=[MessageHandler(Filters.text([CHANGE_PROFILE]), ask_name, pass_user_data=True)],

    # Состояние внутри диалога.
    # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
    states={
        # Функция читает ответ на первый вопрос и задаёт второй.
        -1: [MessageHandler(Filters.text & ~Filters.text([BACK_TO_MENU]),
                            bad_input,
                            pass_user_data=True)],
        0: [MessageHandler(Filters.text & ~Filters.text([BACK_TO_MENU]),
                           ask_sex,
                           pass_user_data=True)],
        1: [MessageHandler(Filters.text & ~Filters.text([BACK_TO_MENU]),
                           ask_form_number,
                           pass_user_data=True)],
        2: [MessageHandler(Filters.text & ~Filters.text([BACK_TO_MENU]),
                           ask_form_letter,
                           pass_user_data=True)],
        3: [MessageHandler(Filters.text & ~Filters.text([BACK_TO_MENU]),
                           ask_for_introduction,
                           pass_user_data=True)],
        4: [MessageHandler(Filters.text & ~Filters.text([BACK_TO_MENU]),
                           ask_for_photo,
                           pass_user_data=True)],
        5: [MessageHandler((Filters.text([CHOOSE_PREVIOUST_PHOTO]) | Filters.photo) & ~Filters.text([BACK_TO_MENU]),
                           ask_for_address,
                           pass_user_data=True)],
        6: [MessageHandler(Filters.text & ~Filters.text([BACK_TO_MENU]),
                           ask_searching_sex,
                           pass_user_data=True)],
        7: [MessageHandler(Filters.text & ~Filters.text([BACK_TO_MENU]),
                           end_registration,
                           pass_user_data=True)]
    },

    # Точка прерывания диалога. В данном случае — команда /stop.
    fallbacks=[MessageHandler(Filters.text([BACK_TO_MENU]), entery_menu, pass_user_data=True)]
)


# ----------------------------------------------- просмотр анкет -------------------------------------------------------
def send_form(update, context, id_tg: int):
    data = get_user_data(id_tg)
    if not data:
        bad_sever_connection(update)
        return False
    context.bot.send_photo(update.message.chat_id, base64.b64decode(data["photo"]))
    context.bot.send_message(update.message.chat_id,
        f"{data['name']}, {data['form_number']}{data['form_char']}\n"
        f"{data['about']}\n"
    )
    return True


def do_what_needed(update: telegram.update.Update, context, user):
    if user["users_liked_ids"]:
        context.bot.send_message(user["chat_id"],
                                 "Этому пользователю вы приглянулись. А как он тебе?")
        send_form(update, context, user["users_liked_ids"][0])
        update.message.reply_text("Как тебе этот человек?",
                                  reply_markup=watching_profiles_keyboard)
        return 1
    else:
        if user["last_watched_id"] == -1:
            user_to_watch = get_user_to_watch(user["id_tg"])
            if not user_to_watch:
                update.message.reply_text(
                    "Похоже, что вы посмотрели все анкеты или сервер бота залагал. Повторите попытку позже.",
                    reply_markup=main_keyboard
                )
                return ConversationHandler.END
            done = post_user_data(id_tg=user["id_tg"], last_watched_id=user_to_watch["id_tg"])
            if not done:
                bad_sever_connection(update)
                return ConversationHandler.END
            if not send_form(update, context, user_to_watch["id_tg"]):
                bad_sever_connection(update)
                return ConversationHandler.END
            update.message.reply_text("Как тебе этот человек?",
                                      reply_markup=watching_profiles_keyboard)

        else:
            done = send_form(update, context, user["last_watched_id"])
            print(done)
            if not done:
                bad_sever_connection(update)
                return ConversationHandler.END
            update.message.reply_text("Как тебе этот человек?",
                                  reply_markup=watching_profiles_keyboard)
        return 2


def start_watching(update, context):
    # проверка на зарегистрированность
    if not is_registred(update.message.from_user.id):
        update.message.reply_text(
            f"сначала нужно создать свою анкету. Нажмите '{CHANGE_PROFILE}'.",
            reply_markup=main_keyboard
        )
        return ConversationHandler.END
    # получение данных пользователя
    user = get_user_data(update.message.from_user.id)
    if not user:
        bad_sever_connection(update)
        return ConversationHandler.END
    # проверка на целостность данных
    if (not user["name"] or
            not user["sex"] or
            not user["photo"] or
            not user["form_number"] or
            not user["form_char"] or
            not user["address"] or
            not user["searching_sex"] or
            not user["about"]):
        update.message.reply_text(
            f"Вы не до конца заполнили анкету. Дозаполните ее нажав на {CHANGE_PROFILE}.",
            reply_markup=main_keyboard
        )
        return ConversationHandler.END
    print("hello")
    return do_what_needed(update, context, user)


def watch_users_liked(update, context):
    if update.message.text not in (LIKE, DISLIKE):
        return 1
    user = get_user_data(update.message.from_user.id)
    if not user:
        bad_sever_connection(update)
        return ConversationHandler.END
    user_matched_data = get_user_data(user["users_liked_ids"][0])
    if not user_matched_data:
        bad_sever_connection(update)
        return ConversationHandler.END
    if update.message.text == LIKE:
        # отправление пользователю, который отправил лайк вторым
        try:
            context.bot.send_photo(update.message.chat_id,
                                   get_address_photo(*get_ll_spn(user_matched_data["address"])))
        except Exception as e:
            print(e)
        context.bot.send_message(user["chat_id"],
            f"У вас мэтч с {user_matched_data['name']}(@{user_matched_data['username']}). "
            f"Адрес этого пользователя: {user_matched_data['address']}"
        )
        # отправление пользователю, у которого лайк был первым
        try:
            context.bot.send_photo(user_matched_data["chat_id"],
                                   get_address_photo(*get_ll_spn(user["address"])))
        except Exception:
            pass
        context.bot.send_message(user_matched_data["chat_id"],
                                 f"У вас мэтч с {user['name']}(@{user['username']}. "
                                 f"Адрес этого пользователя: {user['address']}")
    # добавление пользвателя, который лайкнул, в просмотренных, и удаление его из лайкнувших
    user["watched_ids"].append(user_matched_data["id_tg"])
    user["users_liked_ids"].pop(0)
    print(user["watched_ids"], user["users_liked_ids"])
    done = post_user_data(id_tg=user["id_tg"], users_liked_ids=user["users_liked_ids"],
                          watched_ids=user["watched_ids"])
    if not done:
        bad_sever_connection(update)
        return ConversationHandler.END

    return do_what_needed(update, context, user)


def watch_users_not_liked(update, context):
    if update.message.text not in (LIKE, DISLIKE):
        return 2
    user = get_user_data(update.message.from_user.id)
    if not user:
        bad_sever_connection(update)
        return ConversationHandler.END
    user_liked = get_user_data(user["last_watched_id"])
    if not user_liked:
        bad_sever_connection(update)
        return ConversationHandler.END
    if update.message.text == LIKE:
        user_liked["users_liked_ids"].append(user["id_tg"])
        done = post_user_data(id_tg=user_liked["id_tg"], users_liked_ids=user_liked["users_liked_ids"])
        if not done:
            bad_sever_connection(update)
            return ConversationHandler.END
    user["watched_ids"].append(user["last_watched_id"])
    user["last_watched_id"] = -1
    done = post_user_data(id_tg=user["id_tg"], last_watched_id=user["last_watched_id"], watched_ids=user["watched_ids"])
    if not done:
        bad_sever_connection(update)
        return ConversationHandler.END
    return do_what_needed(update, context, user)


watching_conv_handler = ConversationHandler(

    entry_points=[MessageHandler(Filters.text([WATCH]), start_watching, pass_user_data=True)],

    states={
        1: [MessageHandler(Filters.text & ~Filters.text([BACK_TO_MENU]),
                           watch_users_liked,
                           pass_user_data=True)],
        2: [MessageHandler(Filters.text & ~Filters.text([BACK_TO_MENU]),
                           watch_users_not_liked,
                           pass_user_data=True)]
    },

    fallbacks=[MessageHandler(Filters.text([BACK_TO_MENU]), entery_menu, pass_user_data=True)]
)


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(watching_conv_handler)
    dp.add_handler(edit_conv_handler)
    dp.add_handler(MessageHandler(Filters.text([MENU, BACK_TO_MENU]), entery_menu))
    dp.add_handler(MessageHandler(Filters.text([MY_PROFILE]), my_profile))
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
