from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from lexicon.lexicon_ru import LEXICON_RU


commands_router = Router()

@commands_router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'])