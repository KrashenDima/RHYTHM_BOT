from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton,
    InlineKeyboardMarkup, Message, PhotoSize, ReplyKeyboardRemove
)

from app.bot.states.user_states import FSMFillProfile
from lexicon.lexicon_ru import KEYBOARDS_LEXICON_RU, LEXICON_RU


fill_profile_router = Router()

@fill_profile_router.message(StateFilter(FSMFillProfile.yes_no_fillprofile), 
                             F.text == KEYBOARDS_LEXICON_RU['yes'])
async def process_yes_button(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['fill_name'], reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMFillProfile.fill_name)

@fill_profile_router.message(StateFilter(FSMFillProfile.yes_no_fillprofile),
                             F.text == KEYBOARDS_LEXICON_RU['no'])
async def process_no_button(message: Message):
    await message.answer(text=LEXICON_RU['click_no_button'])

@fill_profile_router.message(StateFilter(FSMFillProfile.yes_no_fillprofile))
async def warning_not_yes_no_btn(message: Message):
    await message.answer(text=LEXICON_RU['warning_yes_no'])

@fill_profile_router.message(StateFilter(FSMFillProfile.fill_name),
                             F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text=LEXICON_RU['fill_city'])
    await state.set_state(FSMFillProfile.fill_city)

@fill_profile_router.message(StateFilter(FSMFillProfile.fill_name))
async def warning_not_name(message: Message):
    await message.answer(text=LEXICON_RU['warning'])

@fill_profile_router.message(StateFilter(FSMFillProfile.fill_city),
                             F.text.isalpha())
async def process_city_sent(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer(text=LEXICON_RU['fill_text'])