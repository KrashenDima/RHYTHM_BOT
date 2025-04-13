from dataclasses import dataclass
from environs import Env

@dataclass
class DatabaseConfig:
    database: str        # название базы данных
    db_host: str         # URL базы данных
    db_port: int
    db_user: str         # имя пользователя базы данных
    db_password: str     # пароль от базы данных

@dataclass
class TgBot:
    token: str               # токен бота
    admin_ids: list[int]     # список id админов бота
    owner_ids: list[int]

@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig

def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS'))),
            owner_ids=list(map(int, env.list('OWNER_IDS')))),
        db=DatabaseConfig(
            database=env('DATABASE'),
            db_host=env('DB_HOST'),
            db_port=env('DB_PORT'),
            db_user=env('DB_USER'), 
            db_password=env('DB_PASSWORD')))

