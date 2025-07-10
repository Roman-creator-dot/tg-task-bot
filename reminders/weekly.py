import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker
from aiogram import Bot

from db.models import User, Task
from db.queries import get_leaderboard_data
from bot.reactions import send_message_with_reactions


# Функция напоминания и отправки топа
import os
from sqlalchemy import select
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker
from db.models import User, Task
from db.queries import get_leaderboard_data  # убедись, что функция импортирована

#  Отправка heartbeat админу (каждую минуту)
async def heartbeat_admin(bot: Bot):
    admin_id = os.getenv("ADMIN_ID")
    if admin_id:
        try:
            await bot.send_message(int(admin_id), "🤖 Ещё живой!")
        except Exception as e:
            print(f"❌ Ошибка при отправке heartbeat админу: {e}")

async def weekly_reminder(bot: Bot, session_maker: async_sessionmaker):
    print("🔁 Запущен weekly_reminder...")

    async with session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"👥 Найдено пользователей: {len(users)}")

        for user in users:
            task_result = await session.execute(
                select(Task).where(Task.user_id == user.id, Task.completed == False)
            )
            active_tasks = task_result.scalars().all()

            try:
                if active_tasks:
                    print(f"📬 Отправляем напоминание пользователю {user.username} (ID: {user.id})")
                    await bot.send_message(
                        user.id,
                        "🔔 Привет! У тебя есть незавершённые задачи. Не забудь их выполнить 💪"
                    )
                else:
                    print(f"✅ Все задачи выполнены у пользователя {user.username} (ID: {user.id})")
                    await bot.send_message(
                        user.id,
                        "🎉 Молодец, все задачи выполнены! Самое время добавить новую 😉"
                    )
            except Exception as e:
                print(f"❌ Ошибка при отправке сообщения пользователю {user.id}: {e}")

        # Получаем данные топа
        print("📊 Получаем данные для таблицы лидеров...")
        leaderboard_data = await get_leaderboard_data()

        if leaderboard_data:
            leaderboard_text = "🏆 Топ участников недели:\n"
            for i, row in enumerate(leaderboard_data, 1):
                leaderboard_text += f"{i}. {row['username']} — {row['score']} очков\n"
        else:
            leaderboard_text = "На этой неделе пока никто не заработал очков 💤"

        # Отправка в групповой чат (ID из переменной окружения)
        group_chat_id = os.getenv("CHAT_ID")
        if group_chat_id:
            try:
                group_chat_id = int(group_chat_id)
                print(f"📤 Отправка топа в групповой чат {group_chat_id}")
                await  send_message_with_reactions(bot,chat_id=group_chat_id, text=leaderboard_text)
            except Exception as e:
                print(f"❌ Ошибка при отправке топа в группу: {e}")
        else:
            print("⚠️ Переменная окружения CHAT_ID не установлена")


# Функция запуска планировщика
def start_reminders(scheduler: AsyncIOScheduler, bot: Bot, session_maker: async_sessionmaker):
    scheduler.add_job(
        weekly_reminder,
        trigger="interval",
        minutes=15,
        args=[bot, session_maker],
    )
    # 🔁 Фейковая отправка админу (каждую минуту)
    scheduler.add_job(
        heartbeat_admin,
        trigger="interval",
        minutes=1,
        args=[bot],
    )
    scheduler.start()
