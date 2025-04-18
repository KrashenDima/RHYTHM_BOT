import logging

from datetime import datetime, timezone
from psycopg import AsyncConnection, AsyncCursor

logger = logging.getLogger(__name__)

class Reactions:

    __tablename__ = "reactions"

    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    # добавление лайка
    async def add(self,
                  *,
                  from_user_id: int,
                  to_user_id: int,
                  reaction_type: str):
           await self.connection.execute(
                 """
                 INSERT INTO reactions(from_user_id, to_user_id, reaction_type)
                 VALUES(%s, %s, %s) ON CONFLICT DO NOTHING;
                 """,
                 (from_user_id, to_user_id, reaction_type))
           logger.info(
                 "Reaction added. db='%s', from_user_id=%s, to_user_id=%s, reaction_type=%s",
                 (self.__tablename__, from_user_id, to_user_id, reaction_type))
    
    async def update_reaction_type(self,
                                   *,
                                   from_user_id: int,
                                   to_user_id: int,
                                   reaction_type: str):
            await self.connection.execute(
                 """
                 UPDATE reactions
                 SET reaction_type = %s
                 WHERE from_user_id = %s AND to_user_id = %s;
            """,
            (reaction_type, from_user_id, to_user_id))


    async def get_reaction(self, 
                        *,
                        from_user_id: int,
                        to_user_id: int,):
           cursor: AsyncCursor = await self.connection.execute(
                 """
                 SELECT from_user_id, to_user_id, reaction_type
                 FROM reactions
                 WHERE from_user_id = %s AND to_user_id = %s;
                 """,
                 (from_user_id, to_user_id))
           return await cursor.fetchone()

           
           
           