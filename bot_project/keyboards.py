from telegram import ReplyKeyboardMarkup
from settings import *
from buttons_text import *

# главное меню
main_keyboard_text = [[WATCH],
                      [CHANGE_PROFILE],
                      [MY_PROFILE]]

main_keyboard = ReplyKeyboardMarkup(main_keyboard_text)


# выбор имени
def get_name_choose_keyboard(prename=""):
    name_choose_keyboard_text = []
    if prename:
        name_choose_keyboard_text.append([prename])
    name_choose_keyboard_text.append([BACK_TO_MENU])

    name_choose_keyboard = ReplyKeyboardMarkup(name_choose_keyboard_text)
    return name_choose_keyboard


# выбор пола
choose_sex_keyboard_text = [[MEN, WOMEN],
                            [BACK_TO_MENU]]

choose_sex_keyboard = ReplyKeyboardMarkup(choose_sex_keyboard_text)


# выбор номера класса
choose_form_number_keyboard_text = [[str(form)] for form in Forms.keys()]
choose_form_number_keyboard_text.append([BACK_TO_MENU])
choose_form_number_keyboard = ReplyKeyboardMarkup(choose_form_number_keyboard_text)


# выбор буквы класса
def get_choose_form_letter_keyboard(form_number):
    choose_form_letter_keyboard_text = [[form_char] for form_char in Forms[form_number]]
    choose_form_letter_keyboard_text.append([BACK_TO_MENU])

    choose_form_letter_keyboard = ReplyKeyboardMarkup(choose_form_letter_keyboard_text)
    return choose_form_letter_keyboard


# выбор искомого пола
choose_searching_sex_keyboard_text = [[WOMEN_SEARCHING, MEN_SEARCHING],
                                      [ALL],
                                      [BACK_TO_MENU]]

choose_searching_sex_keyboard = ReplyKeyboardMarkup(choose_searching_sex_keyboard_text)


# выбор текста анкеты
def get_choose_text_keyboard(already_has_text=False):
    choose_text_keyboard_text = []
    if already_has_text:
        choose_text_keyboard_text.append([CHOOSE_PREVIOUST_TEXT])
    choose_text_keyboard_text.append([BACK_TO_MENU])

    choose_text_keyboard = ReplyKeyboardMarkup(choose_text_keyboard_text)
    return choose_text_keyboard


# выбор фото
def get_choose_photo_keyboard(already_has_photo=False):
    choose_photo_keyboard_text = []
    if already_has_photo:
        choose_photo_keyboard_text.append([CHOOSE_PREVIOUST_PHOTO])
    choose_photo_keyboard_text.append([BACK_TO_MENU])

    choose_photo_keyboard = ReplyKeyboardMarkup(choose_photo_keyboard_text)
    return choose_photo_keyboard


# выбор адреса
def get_choose_address_keyboard(preaddress=""):
    choose_address_keyboard_text = []
    if preaddress:
        choose_address_keyboard_text.append([preaddress])
    choose_address_keyboard_text.append([BACK_TO_MENU])

    choose_address_keyboard = ReplyKeyboardMarkup(choose_address_keyboard_text)
    return choose_address_keyboard


# просмотр анкет
watching_profiles_text = [[LIKE, DISLIKE],
                          [BACK_TO_MENU]]

watching_profiles_keyboard = ReplyKeyboardMarkup(watching_profiles_text)
