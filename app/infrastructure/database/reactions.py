import logging

from datetime import datetime, timezone
from psycopg import AsyncConnection, AsyncCursor

logger = logging.getLogger(__name__)

class Reactions:

    __tablename__ = "reactions"

    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    # добавление лайка
    async def add(self, *, from_user_id: int, to_user_id: int):
           await self.connection.execute(
                 """
                 INSERT INTO reactions(from_user_id, to_user_id)
                 VALUES(%s, %s) ON CONFLICT DO NOTHING;
                 """,
                 (from_user_id, to_user_id))
           
           logger.info(
                 "Reaction added. db='%s', from_user_id=%s, to_user_id=%s",
                 (self.__tablename__, from_user_id, to_user_id))


    async def get_reaction(self, *, from_user_id: int, to_user_id: int,):
           cursor: AsyncCursor = await self.connection.execute(
                 """
                 SELECT 1
                 FROM reactions
                 WHERE from_user_id = %s AND to_user_id = %s;
                 """,
                 (from_user_id, to_user_id))
           return await cursor.fetchone()

           
           
           