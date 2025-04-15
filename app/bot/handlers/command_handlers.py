from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.bot.enums.roles import UserRole
from lexicon.lexicon_ru import LEXICON_RU
from app.infrastructure.database.db import DB
from app.infrastructure.models.users import UsersModel
from app.bot.keyboards.reply_kb import yes_no_keyboard
from app.bot.states.user_states import FSMFillProfile


commands_router = Router()

@commands_router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext, db: DB) -> None:

    user_record: UsersModel | None = await db.users.get_user_record(
        telegram_id=message.from_user.id
    )

    if user_record is None:
        await db.users.add(
            telegram_id=message.from_user.id,
            language=message.from_user.language_code,
            role=UserRole.USER
        )

    await message.answer(text=LEXICON_RU['/start'], reply_markup=yes_no_keyboard)
    await state.set_state(FSMFillProfile.yes_no_fillprofile)