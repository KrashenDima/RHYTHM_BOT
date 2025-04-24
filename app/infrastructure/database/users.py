import logging

from datetime import datetime, timezone
from psycopg import AsyncConnection, AsyncCursor

from app.bot.enums.roles import UserRole
from app.infrastructure.models.users import UsersModel
from app.infrastructure.models.profiles import ProfilesModel

logger = logging.getLogger(__name__)

class _UserDB:
    __tablename1 = "users"
    __tablename2 = "profiles"

    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    # добавление данных о пользователе в таблицу users
    async def add(
            self,
            *,
            telegram_id: int,
            language: str,
            role: UserRole,
            is_alive: bool = True,
            is_blocked: bool = False,
            username: str
    ) -> None:
        
        await self.connection.execute(
            """
            INSERT INTO users(telegram_id, language, role, is_alive, is_blocked, username)
            VALUES(%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
        """,
            (telegram_id, language, role.value, is_alive, is_blocked, username),
        )

        logger.info(
            "User added. db='%s', telegram_id=%d, date_time='%s', "
            "language='%s', role=%s, is_alive=%s, is_blocked=%s",
            self.__tablename1,
            telegram_id,
            datetime.now(timezone.utc),
            language,
            role.value,
            is_alive,
            is_blocked,
        )

    # удаление пользователя из таблицы users
    async def delete(self, *, telegram_id: int) -> None:
        await self.connection.execute(
            """
            DELETE FROM users WHERE telegram_id = %s;
        """,
            (telegram_id,),
        )

        logger.info("User deleted. db='%s', telegram_id='%d'", self.__tablename1, telegram_id)
    
    async def get_user_record(self, *, telegram_id: int) -> UsersModel | None:
        cursor: AsyncCursor = await self.connection.execute(
            """
            SELECT id,
                    telegram_id,
                    created,
                    language,
                    role,
                    is_alive,
                    is_blocked,
                    username
            FROM users
            WHERE users.telegram_id = %s;
        """,
            (telegram_id,),
        )
        # получаем кортеж данных о пользователе
        data = await cursor.fetchone()
        # возвращаем экземпляр класса UsersModel c данными из data или None
        return UsersModel(*data) if data else None
    
    async def update_alive_status(self, *, telegram_id: int, is_alive: bool = True) -> None:
        await self.connection.execute(
            """
            UPDATE users
            SET is_alive = %s
            WHERE telegram_id = %s
        """,
            (is_alive, telegram_id),
        )
        logger.info(
            "User updated. db='%s', user_id=%d, is_alive=%s",
            self.__tablename1,
            telegram_id,
            is_alive,
        )

    async def update_user_lang(self, *, telegram_id: int, user_lang: str) -> None:
        await self.connection.execute(
            """
            UPDATE users
            SET language = %s
            WHERE telegram_id = %s
        """,
            (user_lang, telegram_id),
        )
        logger.info(
            "User updated. db='%s', user_id=%d, language=%s",
            self.__tablename1,
            telegram_id,
            user_lang,
        )

    async def add_profile(
            self,
            *,
            telegram_id: int,
            name: str,
            city: str,
            text: str,
            musician_type: str,
            interest: str,
            photo_url: str,
    ) -> None:
        user = await self.get_user_record(telegram_id=telegram_id)
        await self.connection.execute(
            """
            INSERT INTO profiles(user_id, name, city, text, musician_type, interest, photo_url)
            VALUES(%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
        """,
            (user.id, name, city, text, 
             musician_type, interest, photo_url),
        )

        logger.info(
            "Profile added. db='%s', telegram_id=%d, date_time='%s'",
            self.__tablename2,
            telegram_id,
            datetime.now(timezone.utc),
        ) 
    
    async def delete_profile(self, *, telegram_id: int) -> None:
        user = await self.get_user_record(telegram_id=telegram_id)
        await self.connection.execute(
            """
            DELETE FROM profiles WHERE user_id = %s;
        """,
            (user.id,),
        )

        logger.info("Profile deleted. db='%s', telegram_id='%d'", self.__tablename2, telegram_id)

    async def get_profile_record(self, *, telegram_id: int) -> ProfilesModel | None:
        user = await self.get_user_record(telegram_id=telegram_id)
        cursor: AsyncCursor = await self.connection.execute(
            """
            SELECT id,
                    user_id,
                    name,
                    city,
                    text,
                    musician_type,
                    interest,
                    photo_url,
                    created_at,
                    updated_at
            FROM profiles
            WHERE user_id = %s;
        """,
        (user.id,),
        )
        data = await cursor.fetchone()
        return ProfilesModel(*data) if data else None

    async def get_random_appropriate_profile(self, *, users_id: list[int], 
                                      city: str, interest: str):
        placeholders = ', '.join(['%s'] * len(users_id))
        query = f"""SELECT user_id,
                    name,
                    city,
                    text,
                    photo_url
                    FROM profiles
                    WHERE user_id NOT IN ({placeholders}) AND city = %s AND musician_type = %s
                    ORDER BY RANDOM()
                    LIMIT 1;
        """
        params = users_id + [city.title(), interest]
        cursor: AsyncCursor = await self.connection.execute(query, params)
        return await cursor.fetchone()
    
    async def get_telegram_id_from_profile(self, *, user_id: int):
        cursor: AsyncCursor = await self.connection.execute(
            """
            SELECT telegram_id
            FROM users
            WHERE id = %s;
        """,
        (user_id,))
        telegram_id = await cursor.fetchone()
        return telegram_id[0] if telegram_id else None


