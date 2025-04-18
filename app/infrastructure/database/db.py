from psycopg import AsyncConnection

from app.infrastructure.database.users import _UserDB
from app.infrastructure.database.reactions import Reactions

class DB:
    def __init__(self, connection: AsyncConnection):
        self.users = _UserDB(connection=connection)
        self.reactions = Reactions(connection=connection)