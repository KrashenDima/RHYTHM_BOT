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


    async def get_reaction(self, *, from_user_id: int, to_user_id: int):
           cursor: AsyncCursor = await self.connection.execute(
                 """
                 SELECT 1
                 FROM reactions
                 WHERE from_user_id = %s AND to_user_id = %s;
                 """,
                 (from_user_id, to_user_id))
           return await cursor.fetchone()
    
    async def get_from_users(self, *, to_user_id: int):
          cursor: AsyncCursor = await self.connection.execute(
                """
                SELECT from_user_id
                FROM reactions
                WHERE to_user_id = %s;
                """,
                (to_user_id,))
          return await cursor.fetchall()
    
    async def delete_like(self, *, from_user: int, to_user: int):
          await self.connection.execute(
                """
                DELETE FROM reactions 
                WHERE from_user_id = %s AND to_user_id = %s;
                """,
                (from_user, to_user))

           
           
           