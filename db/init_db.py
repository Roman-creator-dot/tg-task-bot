# init_db.py
import asyncio
from db.base import engine
from .models import Base

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База данных и таблицы успешно созданы.")

if __name__ == "__main__":
    asyncio.run(init())
