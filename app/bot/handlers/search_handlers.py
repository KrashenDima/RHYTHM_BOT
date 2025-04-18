import random

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from app.bot.states.user_states import FSMSearch
from app.infrastructure.database.db import DB
from app.infrastructure.models.profiles import ProfilesModel
from app.bot.keyboards.reply_kb import main_menu_keyboard, like_dislike_keyboard
from lexicon.lexicon_ru import KEYBOARDS_LEXICON_RU, LEXICON_RU


search_router = Router()

# обработчик нажатия кнопки 1. Смотреть анкеты
@search_router.message(StateFilter(FSMSearch.main_menu),
                       F.text == KEYBOARDS_LEXICON_RU['one'])
async def process_main_menu_one(message: Message, 
                                state: FSMContext,
                                db: DB):
    profile_record: ProfilesModel | None = await db.users.get_profile_record(
        telegram_id=message.from_user.id)
    
    if profile_record is not None:
        appropriate_profiles = await db.users.get_appropriate_profiles(
            telegram_id=message.from_user.id,
            city=profile_record.city,
            interest=profile_record.interest
            )
        if not appropriate_profiles:
            await message.answer(text=LEXICON_RU['not_found'])
            await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
        else:
            profile = appropriate_profiles[random.randint(0, len(appropriate_profiles) - 1)]
            await state.update_data(random_profile=profile)
            if profile[-1] is not None:
                await message.answer_photo(photo=[-1],
                                           caption=f'{profile[1]}, {profile[2]}\n{profile[3]}',
                                           reply_markup=like_dislike_keyboard)
                await state.set_state(FSMSearch.search)
            else: 
                await message.answer(text=f'{profile[1]}, {profile[2]}\n{profile[3]}',
                                           reply_markup=like_dislike_keyboard)
                await state.set_state(FSMSearch.search)
    else: 
        await message.answer(text=LEXICON_RU['not_found_you_profile'])

# обработчик нажатия кнопки 2. Моя анкета
@search_router.message(StateFilter(FSMSearch.main_menu),
                       F.text == KEYBOARDS_LEXICON_RU['two'])
async def process_main_menu_two(message: Message, db: DB):
    profile_record: ProfilesModel | None = await db.users.get_profile_record(
        telegram_id=message.from_user.id)
    
    if profile_record is not None:
        name = profile_record.name
        city = profile_record.city
        text = profile_record.text
        photo = profile_record.photo_url
        if photo is None:
             await message.answer(text=f'{name}, {city}\n{text}')
             await message.answer(text=LEXICON_RU['main_menu'])
        else: 
            await message.answer_photo(photo=photo,
                                       caption=f'{name}, {city}\n{text}')
            await message.answer(text=LEXICON_RU['main_menu'])
    else: 
        await message.answer(text=LEXICON_RU['not_found_you_profile'])

@search_router.message(StateFilter(FSMSearch.main_menu))
async def warning_main_menu(message: Message):
    await message.answer(text=LEXICON_RU['warning'])

@search_router.message(StateFilter(FSMSearch.search),
                       F.text.in_({KEYBOARDS_LEXICON_RU['like'],
                                   KEYBOARDS_LEXICON_RU['dislike']}))
async def process_reaction(message: Message, 
                                state: FSMContext,
                                db: DB):
    state_data = state.get_data()

    reaction = db.reactions.get_reaction(
        from_user_id=message.from_user.id,
        to_user_id=state_data['random_profile'])
    
    other_reaction = db.reactions.get_reaction(
            from_user_id=state_data['random_profile'],
            to_user_id=message.from_user.id)

    if reaction is None:
        db.reactions.add(
            from_user_id=message.from_user.id,
            to_user_id=state_data['random_profile'],
            reaction_type=message.text)
        
    else:
        db.reactions.update_reaction_type(
            from_user_id=message.from_user.id,
            to_user_id=state_data['random_profile'],
            reaction_type=message.text)
    

