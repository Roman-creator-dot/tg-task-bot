# Файл: bot/handlers.py
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import os
import sys
from dotenv import load_dotenv

load_dotenv()
# Здесь можно добавить дополнительные переменные окружения или логику инициализации, если нужно
ID_CHAT = os.getenv("CHAT_ID")
print(f"ID_CHAT: {ID_CHAT}")  # Проверяем ID чата

from bot.services import (
    add_user_into_db,
    handle_task_text_received,
    get_weekly_leaderboard,
    get_user_tasks,
    complete_task_by_id
    
)
from bot.keyboards import main_menu_kb, tasks_inline_kb
from bot.states import AddTaskState

# Старт или меню: показать главное меню
async def start_handler(message: Message):
    print("👉 Вызван start_handler")
    await message.answer( "**Добро пожаловать!** 👋\n\n"
        "Здесь мы создаём задачи, выполняем их и получаем баллы за активность.\n\n"
        "📌 **Правила:**\n"
        "• За выполнение задачи — **10 баллов**\n"
        "• За то, что поставил реакцию — **1 балл**\n\n"
        "Следи за задачами, реагируй и зарабатывай очки!\n"
        "Удачи", reply_markup=main_menu_kb())
    await add_user_into_db(message)  # Добавляем пользователя в БД

# Команда: Добавить задачу — переходит в состояние ожидания текста
async def add_task_command(message: Message, state: FSMContext):
    print("👉 Вызван add_task_command")
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer("✏️ Напиши свою задачу:")
    await state.set_state(AddTaskState.waiting_for_text)

# Обработка текста задачи ТОЛЬКО в состоянии ожидания
async def task_text_handler(message: Message, state: FSMContext):
    print("👉 Вызван task_text_handler")
    await handle_task_text_received(message)
    await state.clear()

# Команда: Мои задачи — показывает список с кнопками
async def my_tasks_command(message: Message):
    print("👉 Вызван my_tasks_command")
    tasks = await get_user_tasks(message.from_user.id)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if not tasks:
        await message.answer("У тебя пока нет активных задач ✏️")
    else:
        await message.answer("📋 Твои задачи:", reply_markup=tasks_inline_kb(tasks))

# Обработка кнопки выполнения задачи
async def complete_task_callback(call: CallbackQuery):
    print("👉 Вызван complete_task_callback")
    await complete_task_by_id(call)

# Команда /топ — таблица лидеров
async def leaderboard_handler(message: Message):
    print("👉 Вызван leaderboard_handler")
    text = await get_weekly_leaderboard()
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.bot.send_message(message.chat.id, text=text)

# Команда /chatid — для получения ID чата
async def get_chat_id(message: Message):
    print("👉 Вызван get_chat_id")
    print("Chat ID:", message.chat.id)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(f"Chat ID: `{message.chat.id}`", parse_mode="Markdown")
    
    


# Регистрация всех хендлеров
def register_handlers(dp: Dispatcher):
    print("🔧 Регистрируем хендлеры...")
    dp.message.register(start_handler, Command(commands=["start", "меню"]))
    dp.message.register(add_task_command, F.text == "➕ Добавить задачу")
    dp.message.register(my_tasks_command, F.text == "📋 Мои задачи")
    dp.message.register(task_text_handler, AddTaskState.waiting_for_text)
    dp.callback_query.register(complete_task_callback, F.data.startswith("complete:"))
    dp.message.register(leaderboard_handler, F.text == "📊 топ")
    dp.message.register(get_chat_id, F.text == "/chatid")
