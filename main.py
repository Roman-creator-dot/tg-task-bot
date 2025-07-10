import asyncio
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from reminders.weekly import start_reminders
from db.base import init_db, async_session_maker
from bot.handlers import register_handlers
from bot.reactions import router as reaction_router
from fastapi import FastAPI
import uvicorn

# ✅ Windows loop fix
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ✅ FastAPI-приложение
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "🤖 Бот работает"}

# ✅ Запуск бота
async def start_bot():
    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    print(f"🔐 BOT_TOKEN: {BOT_TOKEN}")
    print(f"💬 CHAT_ID: {CHAT_ID}")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(reaction_router)
    register_handlers(dp)

    await init_db()
    print("🛠️ База данных инициализирована")

    scheduler = AsyncIOScheduler(timezone="Europe/Belgrade")
    start_reminders(scheduler, bot, async_session_maker)
    print("📅 Планировщик запущен")

    print("✅ Polling запущен")
    await dp.start_polling(bot)

# ✅ Главная функция запуска всего приложения
def run():
    loop = asyncio.get_event_loop()
    
    # Запускаем бота как фоновую задачу
    loop.create_task(start_bot())

    # Запускаем FastAPI на том же loop
    port = int(os.environ.get("PORT", 10000))
    config = uvicorn.Config(app=app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)

    print(f"🌐 FastAPI запускается на порту {port}")
    loop.run_until_complete(server.serve())

# ✅ Точка входа
if __name__ == "__main__":
    print("🏁 Старт приложения...")
    try:
        run()
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
    finally:
        print("⚠️ Приложение завершилось")

