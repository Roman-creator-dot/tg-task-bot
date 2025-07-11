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
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import uvicorn

# ✅ Windows loop fix
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ✅ FastAPI-приложение
app = FastAPI()

# ✅ Эндпоинт для проверки Render/UptimeRobot
@app.api_route("/", methods=["GET", "HEAD"])
async def root(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"status": "🤖 Бот работает"}

# ✅ Асинхронная функция запуска бота
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

# ✅ Асинхронная функция запуска FastAPI сервера
async def start_fastapi():
    port = int(os.environ.get("PORT", 10000))
    config = uvicorn.Config(app=app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    print(f"🌐 FastAPI запускается на порту {port}")
    await server.serve()

# ✅ Главная точка запуска всего
async def main():
    await asyncio.gather(
        start_bot(),
        start_fastapi()
    )

# ✅ Точка входа
if __name__ == "__main__":
    print("🏁 Старт приложения...")
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
    finally:
        print("⚠️ Приложение завершилось")


