import pytest
import sys
import os
import asyncio
from unittest.mock import AsyncMock
from psycopg import AsyncConnection, AsyncCursor
from psycopg_pool import AsyncConnectionPool

from app.infrastructure.database.db import DB
from app.infrastructure.connect_to_pg import get_pg_pool
from config_data.config import Config, load_config
from app.bot.enums.roles import UserRole

config: Config = load_config()
user = config.db.db_user
password = config.db.db_password
host = config.db.db_host
port = config.db.db_port
name_db = config.db.database

if sys.platform.startswith("win") or os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.mark.asyncio
async def test_create_profile_db():
    telegram_id = 1111111
    name = 'Dima'
    city = 'Ekaterinburg'
    text = 'Хочу найти барабанщика'
    musician_type = 'группа'
    interest = 'барабаны'
    photo_url = 'bbbbsfgpo,.ler'

    db_pool: AsyncConnectionPool = await get_pg_pool(
        db_name=name_db,
        host=host,
        port=port,
        user=user,
        password=password)

    async with db_pool.connection() as connection:
         async with connection.transaction():
            db = DB(connection)
            db.users.add(
                telegram_id=telegram_id,
                language='ru',
                role=UserRole.USER,
            )
            db.users.add_profile(
                telegram_id=telegram_id,
                name=name,
                city=city,
                text=text,
                musician_type=musician_type,
                interest=interest,
                photo_url=photo_url)

    db_pool.close()