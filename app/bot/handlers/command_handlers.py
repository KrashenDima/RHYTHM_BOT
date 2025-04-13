from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from app.bot.enums.roles import UserRole
from lexicon.lexicon_ru import LEXICON_RU
from app.infrastructure.database.db import DB
from app.infrastructure.models.users import UsersModel


commands_router = Router()

@commands_router.message(CommandStart())
async def process_start_command(message: Message, db: DB) -> None:

    user_record: UsersModel | None = await db.users.get_user_record(
        telegram_id=message.from_user.id
    )

    if user_record is None:
        await db.users.add(
            telegram_id=message.from_user.id,
            language=message.from_user.language_code,
            role=UserRole.USER
        )

    await message.answer(text=LEXICON_RU['/start'])