import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from app.bot.states.user_states import FSMSearch
from app.infrastructure.database.db import DB
from app.infrastructure.models.profiles import ProfilesModel
from app.bot.keyboards.reply_kb import main_menu_keyboard, like_dislike_keyboard
from lexicon.lexicon_ru import KEYBOARDS_LEXICON_RU, LEXICON_RU

logger = logging.getLogger(__name__)

search_router = Router()

# функция получения случайной анкеты, подходящей пользователю
async def get_random_profile(profile_record: ProfilesModel,
                             db: DB,
                             message: Message,
                             state: FSMContext) -> None:
    state_data = await state.get_data()
    updated_list: list[int] = state_data.get("list_of_received_users", [])
    appropriate_profile = await db.users.get_random_appropriate_profile(
            users_id=updated_list,
            city=profile_record.city,
            interest=profile_record.interest)
    
    if not appropriate_profile:
        await message.answer(text=LEXICON_RU['not_found'])
        await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
        await state.set_state(FSMSearch.main_menu)
    else:
        updated_list.append(appropriate_profile[0])
        await state.update_data(list_of_received_users = updated_list)
        
        if appropriate_profile[-1] is not None:
            await message.answer_photo(photo=appropriate_profile[-1],
                                       caption=f'{appropriate_profile[1]}, '
                                       f'{appropriate_profile[2]}\n{appropriate_profile[3]}',
                                       reply_markup=like_dislike_keyboard)
        else: 
            await message.answer(text=f'{appropriate_profile[1]}, '
                                 f'{appropriate_profile[2]}\n{appropriate_profile[3]}',
                                 reply_markup=like_dislike_keyboard)
    

# обработчик нажатия кнопки 1. Смотреть анкеты
@search_router.message(StateFilter(FSMSearch.main_menu),
                       F.text == KEYBOARDS_LEXICON_RU['one'])
async def process_main_menu_one(message: Message, state: FSMContext, db: DB):
    profile_record: ProfilesModel | None = await db.users.get_profile_record(
        telegram_id=message.from_user.id)
    
    if profile_record is not None:
        await state.update_data(list_of_received_users = [message.from_user.id])
        state_data = await state.get_data()
        updated_list: list[int] = state_data.get("list_of_received_users", [])
        appropriate_profile = await db.users.get_random_appropriate_profile(
            users_id=updated_list,
            city=profile_record.city,
            interest=profile_record.interest)
        
        if not appropriate_profile:
            await message.answer(text=LEXICON_RU['not_found'])
            await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
        else:
            logger.debug(f"appropriate_profile[0] = {appropriate_profile[0]}")

            updated_list.append(appropriate_profile[0])
            await state.update_data(list_of_received_users = updated_list)

            if appropriate_profile[-1] is not None:
                await message.answer_photo(photo=appropriate_profile[-1],
                                           caption=f'{appropriate_profile[1]}, '
                                           f'{appropriate_profile[2]}\n{appropriate_profile[3]}',
                                           reply_markup=like_dislike_keyboard)
            else: 
                await message.answer(text=f'{appropriate_profile[1]}, '
                                     f'{appropriate_profile[2]}\n{appropriate_profile[3]}',
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

# обработчик нажатия книпки 3. Лайки
@search_router.message(StateFilter(FSMSearch.main_menu),
                       F.text == KEYBOARDS_LEXICON_RU['three'])




# обработчик некорректного сообщения пользователя в главном меню
@search_router.message(StateFilter(FSMSearch.main_menu))
async def warning_main_menu(message: Message):
    await message.answer(text=LEXICON_RU['warning'])



# обработчик лайка в состоянии поиска
@search_router.message(StateFilter(FSMSearch.search),
                       F.text == KEYBOARDS_LEXICON_RU['like'])
async def process_like(message: Message, state: FSMContext, db: DB):
    state_data = await state.get_data()
    updated_list: list[int] = state_data.get("list_of_received_users", [])
    from_user = message.from_user.id
    to_user = await db.users.get_telegram_id_from_profile(
        user_id = updated_list[-1])
    
    profile_record: ProfilesModel | None = await db.users.get_profile_record(
        telegram_id=from_user)
    other_profile_record: ProfilesModel= await db.users.get_profile_record(
        telegram_id=to_user
    )

    try:
        await db.reactions.add(
            from_user_id=from_user,
            to_user_id=to_user)
        
        is_match = await db.reactions.get_reaction(
            from_user_id=to_user,
            to_user_id=from_user)
        
        if is_match:
            user_record = await db.users.get_user_record(
                telegram_id=from_user)
            other_user_record = await db.users.get_user_record(
                telegram_id=to_user)
            
            await message.answer(
                text=LEXICON_RU['match'] + f'<a href="https://t.me/{other_user_record.username}">{other_profile_record.name}</a>')
            

            await message.bot.send_message(chat_id=to_user, 
                                           text=LEXICON_RU['match_for_other_user_first'])
            name = profile_record.name
            city = profile_record.city
            text = profile_record.text
            photo = profile_record.photo_url
            if photo is None:
                await message.bot.send_message(chat_id=to_user, 
                                               text=f'{name}, {city}\n{text}')
            else: 
                await message.bot.send_photo(chat_id=to_user, 
                                             photo=photo,
                                             caption=f'{name}, {city}\n{text}')
            await message.bot.send_message(chat_id=to_user,
                                           text=LEXICON_RU['match_for_other_user_second'] + 
                                           f'<a href="https://t.me/{user_record.username}">{profile_record.name}</a>')

        await get_random_profile(profile_record=profile_record,
                                 db=db,
                                 message=message,
                                 state=state)

    except Exception as e:
        logger.debug(e)
        await message.answer(text=LEXICON_RU['error_like'])

# обработчик дизлайка в состоянии поиска
@search_router.message(StateFilter(FSMSearch.search),
                       F.text == KEYBOARDS_LEXICON_RU['dislike'])
async def process_dislike(message: Message, state: FSMContext, db: DB):
    profile_record: ProfilesModel | None = await db.users.get_profile_record(
        telegram_id=message.from_user.id)

    try:
        await get_random_profile(profile_record=profile_record,
                                 db=db,
                                 message=message,
                                 state=state)
    except Exception as e:
        logger.debug(e)
        await message.answer(text=LEXICON_RU['error_like'])


# обработчик выхода на гланое меню в состоянии поиска
@search_router.message(StateFilter(FSMSearch.search),
                       F.text == KEYBOARDS_LEXICON_RU['sleep'])
async def process_sleep(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
    await state.set_state(FSMSearch.main_menu)

# обработчик некорректного сообщения в состоянии поиска
@search_router.message(StateFilter(FSMSearch.search))
async def warning_search(message: Message):
    await message.answer(text=LEXICON_RU['warning'])