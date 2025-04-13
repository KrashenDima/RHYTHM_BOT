from dataclasses import dataclass
from datetime import datetime

from app.infrastructure.models.base import BaseModel
from app.bot.enums.roles import UserRole


# класс информации о пользователе
@dataclass
class UsersModel(BaseModel):
    id: int
    telegram_id: int
    created: datetime
    language: str
    role: UserRole
    is_alive: bool
    is_blocked: bool

    def __post_init__(self):
        self.role = UserRole(self.role)