from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from lexicon.lexicon_ru import KEYBOARDS_LEXICON_RU

yes_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['yes'])
no_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['no'])

mus_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['musician'])
mus_group_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['music_group'])
sound_engineer_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['sound_engineer'])

no_photo_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['no_photo'])

one_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['one'])
two_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['two'])
three_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['three'])

like_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['like'])
dislike_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['dislike'])
sleep_btn = KeyboardButton(text=KEYBOARDS_LEXICON_RU['sleep'])

yes_no_keyboard = ReplyKeyboardMarkup(
    keyboard=[[yes_btn, no_btn]],
    one_time_keyboard=True,
    resize_keyboard=True)
musician_type_keyboard = ReplyKeyboardMarkup(
    keyboard=[[mus_btn], [mus_group_btn], [sound_engineer_btn]],
    resize_keyboard=True
)
no_photo_keyboard = ReplyKeyboardMarkup(
    keyboard=[[no_photo_btn]],
    resize_keyboard=True
)
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[one_btn, two_btn, three_btn]],
    resize_keyboard=True
)
like_dislike_keyboard = ReplyKeyboardMarkup(
    keyboard=[[like_btn, dislike_btn, sleep_btn]],
    resize_keyboard=True
)