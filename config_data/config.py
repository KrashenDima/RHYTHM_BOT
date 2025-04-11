from dataclasses import dataclass
from environs import Env

@dataclass
class DatabaseConfig:
    database: str        # название базы данных
    db_host: str         # URL базы данных
    db_user: str         # имя пользователя базы данных
    db_password: str     # пароль от базы данных

@dataclass
class TgBot:
    token: str               # токен бота
    admin_ids: list[int]     # список id админов бота

@dataclass
class Config:
    tg_bot: TgBot

def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS')))))

