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

async def profile_output(message: Message,
                         photo: str | None,
                         name: str,
                         city: str,
                         text: str):
    # если у пользователя есть фото, выдаем фото с текстом, инече просто текст
    if photo is not None:
        await message.answer_photo(photo=photo, caption=f'{name}, {city}\n{text}',
                                   reply_markup=like_dislike_keyboard)
    else: 
        await message.answer(text=f'{name}, {city}\n{text}',
                             reply_markup=like_dislike_keyboard)

# функция получения случайной анкеты, подходящей пользователю
async def get_random_profile(profile_record: ProfilesModel,
                             db: DB,
                             message: Message,
                             state: FSMContext):
    state_data = await state.get_data()
    # из данных состояния получаем пользователей, 
    # которые уже были (чтобы не повторялись анкеты при поиске)
    updated_list: list[int] = state_data.get("list_of_received_users", [])

    # получаем случайную анкету, подходящую пользователю по городу и интересу
    appropriate_profile = await db.users.get_random_appropriate_profile(
            users_id=updated_list,
            city=profile_record.city,
            interest=profile_record.interest)
    if not appropriate_profile:
        await message.answer(text=LEXICON_RU['not_found'])
        await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
        await state.set_state(FSMSearch.main_menu)
    else:
        # добавляем нового полученного пользователя
        updated_list.append(appropriate_profile[0])
        await state.update_data(list_of_received_users = updated_list)
    
        await profile_output(message=message, 
                             photo=appropriate_profile[-1], 
                             name=appropriate_profile[1],
                             city=appropriate_profile[2],
                             text=appropriate_profile[3])

# обработка взаимного лайка
async def process_match(message: Message,
                        db: DB,
                        from_user: int,
                        to_user: int,
                        profile_record: ProfilesModel,
                        other_profile_record: ProfilesModel):
     user_record = await db.users.get_user_record(
                telegram_id=from_user)
     other_user_record = await db.users.get_user_record(
                telegram_id=to_user)
     
     await message.answer(
         text=LEXICON_RU['match'] + 
         f'<a href="https://t.me/{other_user_record.username}">{other_profile_record.name}</a>')
     
     await message.bot.send_message(chat_id=to_user, text=LEXICON_RU['match_for_other_user_first'])
     
     name = profile_record.name
     city = profile_record.city
     text = profile_record.text
     photo = profile_record.photo_url
     
     if photo is None:
        await message.bot.send_message(chat_id=to_user, text=f'{name}, {city}\n{text}')
     else:
        await message.bot.send_photo(chat_id=to_user, photo=photo, 
                                     caption=f'{name}, {city}\n{text}')
        
     await message.bot.send_message(chat_id=to_user,
                                       text=LEXICON_RU['match_for_other_user_second'] + 
                                       f'<a href="https://t.me/{user_record.username}">{profile_record.name}</a>')
    

# обработчик нажатия кнопки 1. Смотреть анкеты
@search_router.message(StateFilter(FSMSearch.main_menu),
                       F.text == KEYBOARDS_LEXICON_RU['one'])
async def process_main_menu_one(message: Message, state: FSMContext, db: DB):
    profile_record: ProfilesModel | None = await db.users.get_profile_record(
        telegram_id=message.from_user.id)
    
    if profile_record is not None:
        # в данных состояния создаём список тех, кого исключить при поиске анкет
        # при нажатии кнопки "смотреть анкеты" первым туда положим id нашего пользователя
        await state.update_data(list_of_received_users = [message.from_user.id])
        state_data = await state.get_data()
        updated_list: list[int] = state_data.get("list_of_received_users", [])

        # получаем случайную анкету, подходящую пользователю по городу и интересу
        appropriate_profile = await db.users.get_random_appropriate_profile(
            users_id=updated_list,
            city=profile_record.city,
            interest=profile_record.interest)
        if not appropriate_profile:
            await message.answer(text=LEXICON_RU['not_found'])
            await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
        else:
            # добавляем нового полученного пользователя
            updated_list.append(appropriate_profile[0])
            await state.update_data(list_of_received_users = updated_list)
            await profile_output(message=message, 
                             photo=appropriate_profile[-1], 
                             name=appropriate_profile[1],
                             city=appropriate_profile[2],
                             text=appropriate_profile[3])
            
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
async def process_main_menu_three(message: Message, state: FSMContext, db: DB):
    likes: list = await db.reactions.get_from_users(message.from_user.id)

    if likes:
        await message.answer(text=LEXICON_RU['likes_count'] + f'{len(likes)}')
        profile_record = await db.users.get_profile_record(telegram_id=likes[0])
        await profile_output(message=message,
                             photo=profile_record.photo_url,
                             name=profile_record.name,
                             city=profile_record.city,
                             text=profile_record.text)
        await state.update_data(likes = likes)
        await state.set_state(FSMSearch.view_likes)
    else: 
        await message.answer(text=LEXICON_RU['no_likes'])
        await message.answer(text=LEXICON_RU['main_menu'], 
                             reply_markup=main_menu_keyboard)


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
    # получаем id пользователя последней полученной анкеты
    to_user = await db.users.get_telegram_id_from_profile(
        user_id = updated_list[-1])
    
    profile_record = await db.users.get_profile_record(
        telegram_id=from_user)
    other_profile_record = await db.users.get_profile_record(
        telegram_id=to_user)

    try:
        # добавляем лайк в БД
        await db.reactions.add(
            from_user_id=from_user,
            to_user_id=to_user)
        # проверяем есть ли взаимный лайк
        is_match = await db.reactions.get_reaction(
            from_user_id=to_user,
            to_user_id=from_user)
        
        if is_match:
            await process_match(message, db, from_user, to_user, profile_record, other_profile_record)
        else: 
            await message.bot.send_message(text=LEXICON_RU['like'])

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

@search_router.message(StateFilter(FSMSearch.view_likes),
                       F.text == KEYBOARDS_LEXICON_RU['like'])
async def process_like_in_view_likes(message: Message,
                                     state: FSMContext,
                                     db: DB):
    state_data = await state.get_data()
    likes: list = state_data.get("likes", [])
    from_user = message.from_user.id
    to_user = likes.pop(0)
    
    if likes:
        profile = await db.users.get_profile_record(
            telegram_id=from_user)
        liked_profile = await db.users.get_profile_record(
            telegram_id=to_user)
        
        await process_match(message=message,
                            db=db,
                            from_user=from_user,
                            to_user=to_user,
                            profile_record=profile,
                            other_profile_record=liked_profile)
        other_profile = await db.users.get_profile_record(
            telegram_id=likes[0])
        await profile_output(message=message,
                             photo=other_profile.photo_url,
                             name=other_profile.name,
                             city=other_profile.city,
                             text=other_profile.text)
        await state.update_data(likes = likes)
    else:
        await message.answer(text=LEXICON_RU['no_more_likes'])
        await message.answer(text=LEXICON_RU['main_menu'], 
                             reply_markup=main_menu_keyboard)
        await state.set_state(FSMSearch.main_menu)
