import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from sqlalchemy import text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from reminders.weekly import start_reminders
from db.base import init_db, async_session_maker
from bot.handlers import register_handlers
from bot.reactions import router as reaction_router
from aiohttp import web
from fastapi import FastAPI
import uvicorn
import asyncio
import threading


if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



# FasrAPI  что бы бот не засыпал    
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "🤖 Бот работает"} 
# 🔹 Запуск FastAPI в отдельном потоке
def run_fastapi():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
# Загружаем переменные окружения из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(f"BOT_TOKEN: {BOT_TOKEN}")  # Проверяем токен
ID_CHAT = os.getenv("CHAT_ID")
print(f"ID_CHAT: {ID_CHAT}")  # Проверяем ID чата

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())



dp.include_router(reaction_router)

# Регистрируем все хендлеры
register_handlers(dp)



# Простой хендлер для отладки
#@dp.message()
#async def echo_all_messages(message: types.Message):
#    print(f"📩 Получено сообщение: {message.text}")
#    await message.answer("Бот работает, но команда не распознана.")

async def main():
    await init_db()  # Инициализация базы данных
    print("Бот запущен с Polling ✅")
    scheduler = AsyncIOScheduler(timezone="Europe/Belgrade")  # Создаем планировщик задач
    start_reminders(scheduler, bot, async_session_maker)
    await dp.start_polling(bot) # Запуск polling

if __name__ == "__main__":
        # 🔸 Запуск FastAPI в отдельном потоке
    threading.Thread(target=run_fastapi).start()
    #запуск бота
    asyncio.run(main())
