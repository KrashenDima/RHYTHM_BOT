from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from lexicon.lexicon_ru import KEYBOARDS_LEXICON_RU

yes_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['yes'])
no_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['no'])

yes_no_keyboard = ReplyKeyboardMarkup(
    keyboard=[[yes_btn, no_btn]],
    one_time_keyboard=True,
    resize_keyboard=True)