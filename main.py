import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_data.config import Config, load_config
from app.bot.handlers import command_handlers

# Инициализируем логгер
logger = logging.getLogger(__name__)

async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    
    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    config: Config = load_config()

    print(config.tg_bot.token)
    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(command_handlers.commands_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
