from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton,
    InlineKeyboardMarkup, Message, PhotoSize, ReplyKeyboardRemove
)

from app.bot.states.user_states import FSMFillProfile
from app.infrastructure.database.db import DB
from app.infrastructure.models.profiles import ProfilesModel
from app.bot.keyboards.reply_kb import musician_type_keyboard, no_photo_keyboard
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
    await state.set_state(FSMFillProfile.fill_text)

@fill_profile_router.message(StateFilter(FSMFillProfile.fill_city))
async def warning_not_city(message: Message):
    await message.answer(text=LEXICON_RU['warning'])

@fill_profile_router.message(StateFilter(FSMFillProfile.fill_text))
async def process_text_sent(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(text=LEXICON_RU['fill_musician_type'], 
                         reply_markup=musician_type_keyboard)
    await state.set_state(FSMFillProfile.fill_musician_type)

@fill_profile_router.message(StateFilter(FSMFillProfile.fill_musician_type),
                             F.text.in_({KEYBOARDS_LEXICON_RU['musician'],
                                         KEYBOARDS_LEXICON_RU['usic_group'],
                                         KEYBOARDS_LEXICON_RU['sound_engineer']}))
async def process_musician_type_button(message: Message, state: FSMContext):
    await state.update_data(musician_type=message.text)
    await message.answer(text=LEXICON_RU['fill_interest'])
    await state.set_state(FSMFillProfile.fill_interest)

@fill_profile_router.message(StateFilter(FSMFillProfile.fill_musician_type))
async def warning_no_musician_type(message: Message):
    await message.answer(text=LEXICON_RU['warning'])

@fill_profile_router.message(StateFilter(FSMFillProfile.fill_interest),
                             F.text.in_({KEYBOARDS_LEXICON_RU['musician'],
                                         KEYBOARDS_LEXICON_RU['usic_group'],
                                         KEYBOARDS_LEXICON_RU['sound_engineer']}))
async def process_interest_button(message: Message, state: FSMContext):
    await state.update_data(interest=message.text)
    await message.answer(text=LEXICON_RU['upload_photo'], reply_markup=no_photo_keyboard)
    await state.set_state(FSMFillProfile.upload_photo)

@fill_profile_router.message(StateFilter(FSMFillProfile.fill_interest))
async def warning_no_interest(message: Message):
    await message.answer(text=LEXICON_RU['warning'])

@fill_profile_router.message(StateFilter(FSMFillProfile.upload_photo),
                             F.photo[-1].as_('largest_photo'))
async def process_upload_photo(message: Message, state: FSMContext,
                               largest_photo: PhotoSize, db: DB):
    await state.update_data(photo_id=largest_photo.file_id)
    profile_data = await state.get_data()
    profiles_record: ProfilesModel | None = await db.users.get_profile_record(
        telegram_id=message.from_user.id
    )

    if profiles_record is None:
        await db.users.add_profile(
            telegram_id=message.from_user.id,
            name=profile_data['name'],
            city=profile_data['city'],
            text=profile_data['text'],
            musician_type=profile_data['musician_type'],
            interest=profile_data['interest'],
            photo_url=profile_data['photo_id']
        )
        





