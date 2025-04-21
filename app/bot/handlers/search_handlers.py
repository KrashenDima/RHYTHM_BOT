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
        appropriate_profile = await db.users.get_random_appropriate_profiles(
            telegram_id=message.from_user.id,
            city=profile_record.city,
            interest=profile_record.interest)
        
        if not appropriate_profile:
            await message.answer(text=LEXICON_RU['not_found'])
            await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
        else:
            appropriate_profile_id = await db.users.get_telegram_id_from_profile(appropriate_profile[0])
            await state.update_data(random_profile_id=appropriate_profile_id)
            if appropriate_profile[-1] is not None:
                await message.answer_photo(photo=[-1],
                                           caption=f'{appropriate_profile[1]}, {appropriate_profile[2]}\n{appropriate_profile[3]}',
                                           reply_markup=like_dislike_keyboard)
                await state.set_state(FSMSearch.search)
            else: 
                await message.answer(text=f'{appropriate_profile[1]}, {appropriate_profile[2]}\n{appropriate_profile[3]}',
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
                       F.text == KEYBOARDS_LEXICON_RU['like'])
async def process_like(message: Message, 
                           state: FSMContext,
                           db: DB):
    state_data = await state.get_data()
    from_user = message.from_user.id
    to_user = state_data['random_profile_id']
    profile_record: ProfilesModel | None = await db.users.get_profile_record(
        telegram_id=message.from_user.id)

    try:
        await db.reactions.add(
            from_user_id=from_user,
            to_user_id=to_user)
        
        is_match = await db.reactions.get_reaction(
            from_user_id=to_user,
            to_user_id=from_user)
        
        if is_match:
            await message.answer(text=KEYBOARDS_LEXICON_RU['match'])
            await message.bot.send_message(text=KEYBOARDS_LEXICON_RU['match'])
        
        appropriate_profile = await db.users.get_random_appropriate_profiles(
            telegram_id=message.from_user.id,
            city=profile_record.city,
            interest=profile_record.interest)
        
        if not appropriate_profile:
            await message.answer(text=LEXICON_RU['not_found'])
            await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
        else:
            appropriate_profile_id = await db.users.get_telegram_id_from_profile(appropriate_profile[0])
            await state.update_data(random_profile_id=appropriate_profile_id)
            if appropriate_profile[-1] is not None:
                await message.answer_photo(photo=[-1],
                                           caption=f'{appropriate_profile[1]}, {appropriate_profile[2]}\n{appropriate_profile[3]}',
                                           reply_markup=like_dislike_keyboard)
            else: 
                await message.answer(text=f'{appropriate_profile[1]}, {appropriate_profile[2]}\n{appropriate_profile[3]}',
                                           reply_markup=like_dislike_keyboard)

    except Exception as e:
        await message.answer(text=LEXICON_RU['error_like'])

@search_router.message(StateFilter(FSMSearch.search),
                       F.text == KEYBOARDS_LEXICON_RU['dislike'])
async def process_dislike(message: Message, state: FSMContext,
                          db: DB):
    profile_record: ProfilesModel | None = await db.users.get_profile_record(
        telegram_id=message.from_user.id)
    
    appropriate_profile = await db.users.get_random_appropriate_profiles(
            telegram_id=message.from_user.id,
            city=profile_record.city,
            interest=profile_record.interest)
    
    if not appropriate_profile:
        await message.answer(text=LEXICON_RU['not_found'])
        await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
    else:
        appropriate_profile_id = await db.users.get_telegram_id_from_profile(appropriate_profile[0])
        await state.update_data(random_profile_id=appropriate_profile_id)
        
        if appropriate_profile[-1] is not None:
            await message.answer_photo(photo=[-1],
                                       caption=f'{appropriate_profile[1]}, {appropriate_profile[2]}\n{appropriate_profile[3]}',
                                       reply_markup=like_dislike_keyboard)
        else: 
            await message.answer(text=f'{appropriate_profile[1]}, {appropriate_profile[2]}\n{appropriate_profile[3]}',
                                           reply_markup=like_dislike_keyboard)
            
@search_router.message(StateFilter(FSMSearch.search),
                       F.text == KEYBOARDS_LEXICON_RU['sleep'])
async def process_sleep(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
    await state.set_state(FSMSearch.main_menu)

@search_router.message(StateFilter(FSMSearch.search))
async def warning_search(message: Message):
    await message.answer(text=LEXICON_RU['warning'])