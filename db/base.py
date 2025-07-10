# Файл: db/base.py
# Создание асинхронного движка SQLAlchemy и сессий

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from db.models import Base
import os

# URL подключения к базе данных (лучше хранить в .env)
#DATABASE_URL = "postgresql+asyncpg://postgres:LOKO2000@localhost:5432/task_bot_db"

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not loaded. Проверь .env файл и путь к нему")
# Создаём асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаём фабрику сессий (async сессии)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Функция для создания таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

