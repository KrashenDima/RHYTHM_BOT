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

async def show_main_menu(message: Message) -> None:
    """Отображает главное меню."""
    await message.answer(
        text=LEXICON_RU["main_menu"],
        reply_markup=main_menu_keyboard
    )

async def send_profile(
        message: Message,
        photo: str | None,
        name: str,
        city: str,
        text: str):
    """Отправляет профиль пользователю с фото (если есть) и текстом."""
    profile_text = f"{name}, {city}\n{text}"

    # если у пользователя есть фото, выдаем фото с текстом, инече просто текст
    if photo:
        await message.answer_photo(
            photo=photo,
            caption=profile_text,
            reply_markup=like_dislike_keyboard
        )
    else:
        await message.answer(
            text=profile_text,
            reply_markup=like_dislike_keyboard
        )

async def get_random_profile(
        profile_record: ProfilesModel,
        db: DB,
        message: Message,
        state: FSMContext):
    """Получает и отображает случайный подходящий профиль."""
    state_data = await state.get_data()
    excluded_users: list[int] = state_data.get("excluded_users", [])

    appropriate_profile = await db.users.get_random_appropriate_profile(
        users_id=excluded_users,
        city=profile_record.city,
        interest=profile_record.interest
    )

    if not appropriate_profile:
        await message.answer(text=LEXICON_RU["not_found"])
        await show_main_menu(message)
        await state.set_state(FSMSearch.main_menu)
        return

    excluded_users.append(appropriate_profile[0])
    await state.update_data(excluded_users=excluded_users)

    await send_profile(
        message=message,
        photo=appropriate_profile[-1],
        name=appropriate_profile[1],
        city=appropriate_profile[2],
        text=appropriate_profile[3]
    )

async def handle_match(
        message: Message,
        db: DB,
        from_user_id: int,
        to_user_id: int,
        current_profile: ProfilesModel,
        matched_profile: ProfilesModel
        ) -> None:
    """Обрабатывает взаимный лайк (матч) между пользователями."""
    current_user = await db.users.get_user_record(telegram_id=from_user_id)
    matched_user = await db.users.get_user_record(telegram_id=to_user_id)
    
    # Уведомление текущего пользователя
    await message.answer(
        text=LEXICON_RU["match"] + 
        f'<a href="https://t.me/{matched_user.username}">{matched_profile.name}</a>'
    )
    
    # Уведомление совпавшего пользователя
    await message.bot.send_message(
        chat_id=to_user_id,
        text=LEXICON_RU["match_for_other_user_first"]
    )
    
    # Отправка профиля совпавшему пользователю
    await send_profile(
        message=Message(chat_id=to_user_id),
        name=current_profile.name,
        city=current_profile.city,
        text=current_profile.text,
        photo=current_profile.photo_url
    )
    
    await message.bot.send_message(
        chat_id=to_user_id,
        text=LEXICON_RU["match_for_other_user_second"] + 
        f'<a href="https://t.me/{current_user.username}">{current_profile.name}</a>'
    )
    

@search_router.message(StateFilter(FSMSearch.main_menu),
                       F.text == KEYBOARDS_LEXICON_RU['one'])
async def process_main_menu_one(message: Message, state: FSMContext, db: DB):
     """Обработчик кнопки 'Смотреть анкеты'."""
     profile = await db.users.get_profile_record(telegram_id=message.from_user.id)
     
     if not profile:
        await message.answer(text=LEXICON_RU["not_found_you_profile"])
        return
     await state.update_data(excluded_users=[message.from_user.id])
     await get_random_profile(profile, db, message, state)
     await state.set_state(FSMSearch.search)

# обработчик нажатия кнопки 2. Моя анкета
@search_router.message(StateFilter(FSMSearch.main_menu),
                       F.text == KEYBOARDS_LEXICON_RU['two'])
async def process_main_menu_two(message: Message, db: DB):
    """Обработчик кнопки 'Моя анкета'."""
    profile = await db.users.get_profile_record(telegram_id=message.from_user.id)
    
    if not profile:
        await message.answer(text=LEXICON_RU["not_found_you_profile"])
        return

    await send_profile(
        message=message,
        name=profile.name,
        city=profile.city,
        text=profile.text,
        photo=profile.photo_url
    )
    await show_main_menu(message)

@search_router.message(StateFilter(FSMSearch.main_menu),
                       F.text == KEYBOARDS_LEXICON_RU['three'])
async def process_main_menu_three(message: Message, state: FSMContext, db: DB):
    """Обработчик кнопки 'Лайки'."""
    likes = await db.reactions.get_from_users(to_user_id=message.from_user.id)
    
    if not likes:
        await message.answer(text=LEXICON_RU["no_likes"])
        await show_main_menu(message)
        return

    await message.answer(text=LEXICON_RU["likes_count"] + f"{len(likes)}")
    
    profile = await db.users.get_profile_record(telegram_id=likes[0][0])
    await send_profile(
        message=message,
        name=profile.name,
        city=profile.city,
        text=profile.text,
        photo=profile.photo_url
    )
    
    await state.set_state(FSMSearch.view_likes)

@search_router.message(StateFilter(FSMSearch.main_menu))
async def warning_main_menu(message: Message):
    """Обработчик некорректного сообщения пользователя в главном меню"""
    await message.answer(text=LEXICON_RU['warning'])


@search_router.message(StateFilter(FSMSearch.search),
                       F.text == KEYBOARDS_LEXICON_RU['like'])
async def process_like(message: Message, state: FSMContext, db: DB):
    """Обработчик лайка в состоянии поиска."""
    state_data = await state.get_data()
    excluded_users: list[int] = state_data.get("excluded_users", [])
    
    from_user_id = message.from_user.id
    to_user_id = await db.users.get_telegram_id_from_profile(user_id=excluded_users[-1])
    
    try:
        await db.reactions.add(
            from_user_id=from_user_id,
            to_user_id=to_user_id
        )
        
        current_profile = await db.users.get_profile_record(telegram_id=from_user_id)
        liked_profile = await db.users.get_profile_record(telegram_id=to_user_id)
        
        is_match = await db.reactions.get_reaction(
            from_user_id=to_user_id,
            to_user_id=from_user_id
        )
        
        if is_match:
            await handle_match(
                message, db, from_user_id, to_user_id,
                current_profile, liked_profile
            )
        else:
            await message.bot.send_message(
                chat_id=to_user_id,
                text=LEXICON_RU["like"]
            )
        
        await get_random_profile(current_profile, db, message, state)
    except Exception as e:
        logger.error(f"Error processing like: {e}")
        await message.answer(text=LEXICON_RU["error_like"])

@search_router.message(StateFilter(FSMSearch.search),
                       F.text == KEYBOARDS_LEXICON_RU['dislike'])
async def process_dislike(message: Message, state: FSMContext, db: DB):
    """Обработчик дизлайка в состоянии поиска."""
    profile = await db.users.get_profile_record(telegram_id=message.from_user.id)
    
    try:
        await get_random_profile(profile, db, message, state)
    except Exception as e:
        logger.error(f"Error processing dislike: {e}")
        await message.answer(text=LEXICON_RU["error_like"])


@search_router.message(StateFilter(FSMSearch.search),
                       F.text == KEYBOARDS_LEXICON_RU['sleep'])
async def process_sleep(message: Message, state: FSMContext):
    """Обработчик выхода на гланое меню в состоянии поиска"""
    await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
    await state.set_state(FSMSearch.main_menu)

@search_router.message(StateFilter(FSMSearch.search))
async def warning_search(message: Message):
    """Обработчик некорректного сообщения в состоянии поиска"""
    await message.answer(text=LEXICON_RU['warning'])

@search_router.message(StateFilter(FSMSearch.view_likes),
                       F.text == KEYBOARDS_LEXICON_RU['like'])
async def process_like_in_view_likes(message: Message,
                                     state: FSMContext,
                                     db: DB):
    """Обработка лайка в состоянии просмотра лайков"""
    likes: list = await db.reactions.get_from_users(
        to_user_id=message.from_user.id)
    from_user = message.from_user.id
    to_user = likes[0][0]
    
    profile = await db.users.get_profile_record(
        telegram_id=from_user)
    liked_profile = await db.users.get_profile_record(
        telegram_id=to_user)
    await handle_match(message=message,
                        db=db,
                        from_user=from_user,
                        to_user=to_user,
                        profile_record=profile,
                        other_profile_record=liked_profile)
    await db.reactions.delete_like(from_user=to_user, to_user=from_user)
    await db.reactions.delete_like(from_user=from_user, to_user=to_user)


    new_likes: list = await db.reactions.get_from_users(
        to_user_id=message.from_user.id)
    if new_likes:
        other_profile = await db.users.get_profile_record(
            telegram_id=new_likes[0][0])
        await send_profile(message=message,
                             photo=other_profile.photo_url,
                             name=other_profile.name,
                             city=other_profile.city,
                             text=other_profile.text)
    else:
        await message.answer(text=LEXICON_RU['no_more_likes'])
        await message.answer(text=LEXICON_RU['main_menu'], 
                             reply_markup=main_menu_keyboard)
        await state.set_state(FSMSearch.main_menu)

@search_router.message(StateFilter(FSMSearch.view_likes),
                       F.text == KEYBOARDS_LEXICON_RU['dislike'])
async def process_dislike_in_view_likes(message: Message,
                                        state: FSMContext,
                                        db: DB):
    """Обработка дизлайка в состоянии просмотра лайков"""
    likes: list = await db.reactions.get_from_users(
        to_user_id=message.from_user.id)
    await db.reactions.delete_like(from_user=likes[0][0], 
                                   to_user=message.from_user.id)
    new_likes: list = await db.reactions.get_from_users(
        to_user_id=message.from_user.id)

    if new_likes:
        other_profile = await db.users.get_profile_record(
            telegram_id=new_likes[0][0])
        await send_profile(message=message,
                           photo=other_profile.photo_url,
                           name=other_profile.name,
                           city=other_profile.city,
                           text=other_profile.text)
    else:
        await message.answer(text=LEXICON_RU['no_more_likes'])
        await message.answer(text=LEXICON_RU['main_menu'], 
                             reply_markup=main_menu_keyboard)
        await state.set_state(FSMSearch.main_menu)

@search_router.message(StateFilter(FSMSearch.view_likes),
                       F.text == KEYBOARDS_LEXICON_RU['sleep'])
async def process_sleep_in_view_likes(message: Message, state: FSMContext):
    """Обработка выхода из просмотра лайков"""
    await message.answer(text=LEXICON_RU['main_menu'], 
                         reply_markup=main_menu_keyboard)
    await state.set_state(FSMSearch.main_menu)

@search_router.message(StateFilter(FSMSearch.view_likes))
async def warning_in_view_likes(message: Message):
    """Обработка некорректного сообщения в состоянии просмотра лайков"""
    await message.answer(text=LEXICON_RU['warning'])