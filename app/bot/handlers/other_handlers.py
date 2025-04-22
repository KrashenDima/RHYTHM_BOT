from aiogram import Router, F
from aiogram.types import Message

from lexicon.lexicon_ru import LEXICON_RU

other_router = Router()

@other_router.message()
async def process_something_unclear(message: Message):
    await message.answer(text=LEXICON_RU['something_unclear'])