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
            if profile[-1] is not None:
                await message.answer_photo(photo=profile[-1],
                                           caption=f'{profile[0]}, {profile[1]}\n'
                                           f'{profile[2]}',
                                           reply_markup=like_dislike_keyboard)
                await state.set_state(FSMSearch.search)
            else: 
                await message.answer(text=f'{profile[0]}, {profile[1]}\n'
                                           f'{profile[2]}',
                                           reply_markup=like_dislike_keyboard)
                await state.set_state(FSMSearch.search)
    else: 
        await message.answer(text=LEXICON_RU['not_found_you_profile'])


