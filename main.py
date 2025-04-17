import asyncio
import logging
import sys
import os
import psycopg_pool

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import Config, load_config
from app.bot.handlers import command_handlers, fill_profile_handlers
from app.bot.middlewares.database import DataBaseMiddleware
from app.infrastructure.connect_to_pg import get_pg_pool

# Конфигурируем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

# Инициализируем логгер
logger = logging.getLogger(__name__)

if sys.platform.startswith("win") or os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    config: Config = load_config()

    storage = MemoryStorage()

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    db_pool : psycopg_pool.AsyncConnectionPool = await get_pg_pool(
        db_name=config.db.database,
        host=config.db.db_host,
        port=config.db.db_port,
        user=config.db.db_user,
        password=config.db.db_password
    )

    logger.info("Including routers")
    dp.include_router(command_handlers.commands_router)
    dp.include_router(fill_profile_handlers.fill_profile_router)

    logger.info("Including middlewares")
    dp.update.middleware(DataBaseMiddleware())


    try:
        await dp.start_polling(bot, _db_pool = db_pool)
    except Exception as e: 
        logger.exception(e)
    finally:
        await db_pool.close()
        logger.info("Connection to Postgres closed")


if __name__ == "__main__":
    asyncio.run(main())
