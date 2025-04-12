from psycopg import AsyncConnection

from app.infrastructure.database.users import _UserDB

class DB:
    def __init__(self, connection: AsyncConnection):
        self.users = _UserDB(connection=connection)