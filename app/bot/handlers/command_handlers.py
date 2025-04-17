from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.bot.enums.roles import UserRole
from lexicon.lexicon_ru import LEXICON_RU
from app.infrastructure.database.db import DB
from app.infrastructure.models.users import UsersModel
from app.infrastructure.models.profiles import ProfilesModel
from app.bot.keyboards.reply_kb import yes_no_keyboard, main_menu_keyboard
from app.bot.states.user_states import FSMFillProfile, FSMSearch


commands_router = Router()

@commands_router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext, db: DB) -> None:

    user_record: UsersModel | None = await db.users.get_user_record(
        telegram_id=message.from_user.id
    )
    profile_record: ProfilesModel | None = await db.users.get_profile_record(
        telegram_id=message.from_user.id
    )

    if user_record is None:
        await db.users.add(
            telegram_id=message.from_user.id,
            language=message.from_user.language_code,
            role=UserRole.USER
        )
    if profile_record is None:
        await message.answer(text=LEXICON_RU['/start'], reply_markup=yes_no_keyboard)
        await state.set_state(FSMFillProfile.yes_no_fillprofile)
    else: 
        await message.answer_photo(photo=profile_record.photo_url,
                               caption=f'{profile_record.name}, {profile_record.city}\n\n'
                               f'{profile_record.text}')
        await message.answer(text=LEXICON_RU['main_menu'], reply_markup=main_menu_keyboard)
        await state.set_state(FSMSearch.main_menu)