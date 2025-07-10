import asyncio
import os
import sys
from multiprocessing import Process
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from sqlalchemy import text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from reminders.weekly import start_reminders
from db.base import init_db, async_session_maker
from bot.handlers import register_handlers
from bot.reactions import router as reaction_router
from fastapi import FastAPI
import uvicorn

# ✅ Настройка Windows loop (если локально)
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ✅ FastAPI-приложение для Render
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "🤖 Бот работает"}

# ✅ Отдельная функция запуска FastAPI
def run_fastapi():
    port = int(os.environ.get("PORT", 10000))
    # "main:app" — указывает FastAPI, где искать объект app
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")

# ✅ Основной async-функция запуска бота
async def main():
    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    print(f"BOT_TOKEN: {BOT_TOKEN}")
    print(f"CHAT_ID: {CHAT_ID}")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(reaction_router)
    register_handlers(dp)

    await init_db()
    print("✅ Polling запущен")

    scheduler = AsyncIOScheduler(timezone="Europe/Belgrade")
    start_reminders(scheduler, bot, async_session_maker)

    await dp.start_polling(bot)

# ✅ Точка входа
if __name__ == "__main__":
    # 🟡 Запускаем FastAPI сервер в отдельном процессе
    Process(target=run_fastapi).start()
    # 🟢 Запускаем основной event loop для бота
    asyncio.run(main())
