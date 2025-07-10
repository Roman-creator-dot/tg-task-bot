from aiogram.types import Message, CallbackQuery
from db.queries import (
    add_task_to_db,
    add_user,
    mark_task_complete,
    get_user_active_tasks,
    get_leaderboard_data,
)
from bot.reaction_utils import get_reaction, get_all_emojis_for_message
from bot.reactions import send_message_with_reactions  # Импортируем функцию реакции
import os

ID_CHAT = os.getenv("CHAT_ID")
print(f"ID_CHAT: {ID_CHAT}")  # Проверяем ID чата  

# Добавление пользователя
async def add_user_into_db(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    await add_user(user_id, username)
 

# Добавление задачи с публикацией в группу
async def handle_task_text_received(message: Message):
    text = message.text.strip()
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    await add_task_to_db(user_id=user_id, username=username, text=text)
    await message.answer("Задача сохранена ✅")

    group_chat_id = ID_CHAT# Или ID вашей группы
    full_text = f"📌 @{username} добавил задачу: {text}"
    await send_message_with_reactions(message.bot, group_chat_id, full_text)


# Получение активных задач
async def get_user_tasks(user_id: int):
    return await get_user_active_tasks(user_id)


# Выполнение задачи + публикация в чат
async def complete_task_by_id(call: CallbackQuery):
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.full_name

    task_id = int(call.data.split(":")[1])
    task_text = await mark_task_complete(task_id, user_id)

    if task_text:
        await call.answer("Задача выполнена 🎉")
        text = f"✅ @{username} выполнил задачу: {task_text}"
        await send_message_with_reactions(call.bot, ID_CHAT, text)
    else:
        await call.answer("Ошибка. Задача не найдена или уже выполнена.", show_alert=True)


# Лидерборд
async def get_weekly_leaderboard():
    data = await get_leaderboard_data()
    if not data:
        return "Пока нет данных по очкам. 💤"

    text = "🏆 Топ участников недели:\n"
    for i, row in enumerate(data, 1):
        text += f"{i}. {row['username']} — {row['score']} очков\n"
    return text
