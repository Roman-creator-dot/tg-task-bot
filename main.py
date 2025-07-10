from multiprocessing import Process
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
    print(f"🌐 FastAPI запускается на порту {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")

# ✅ Основной async-функция запуска бота
async def main():
    try:
        print("🚀 Запуск main()")
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

    except Exception as e:
        print(f"❌ ОШИБКА в main(): {e}")

    finally:
        print("⚠️ main() завершился — это не должно происходить!")

# ✅ Точка входа
if __name__ == "__main__":
    print("🏁 Старт приложения...")
    # 🟡 Запускаем FastAPI сервер в отдельном процессе
    Process(target=run_fastapi).start()

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Ошибка на уровне запуска: {e}")
    finally:
        print("⚠️ Приложение полностью завершилось")
