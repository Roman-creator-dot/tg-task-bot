# Файл: db/queries.py
# Здесь находятся функции для работы с базой данных

from db.models import Task, User,Reaction
from db.base import async_session_maker
from sqlalchemy import select, update, func


async def add_user(user_id: int, username: str):
    print(f"Попытка добавить пользователя {user_id} в БД")  # Логирование
    async with async_session_maker() as session:
        user = await session.get(User, user_id)
        if not user:
            print(f"Пользователь {user_id} не найден, создаём нового.")  # Логирование
            user = User(id=user_id, username=username, score=0)
            session.add(user)
            await session.commit()
        else:
            print(f"Пользователь {user_id} уже существует.")  # Логирование

# Добавление новой задачи в БД
async def add_task_to_db(user_id: int, username: str, text: str):
    print(f"Попытка добавить задачу для пользователя {user_id}: {text}")  # Логирование
    async with async_session_maker() as session:
        # Убедимся, что пользователь существует
        user = await session.get(User, user_id)
        if not user:
            print(f"Пользователь {user_id} не найден, создаём нового.")  # Логирование
            user = User(id=user_id, username=username, score=0)
            session.add(user)

        task = Task(user_id=user_id, text=text)
        session.add(task)
        await session.commit()
        print(f"Задача для пользователя {user_id} добавлена: {text}")  # Логирование

# Получение активных задач пользователя
async def get_user_active_tasks(user_id: int):
    print(f"Запрос активных задач для пользователя {user_id}")  # Логирование
    async with async_session_maker() as session:
        result = await session.execute(
            select(Task).where(Task.user_id == user_id, Task.completed == False)
        )
        tasks = result.scalars().all()
        print(f"Найдено {len(tasks)} активных задач для пользователя {user_id}")  # Логирование
        return tasks

# Отметить задачу выполненной, вернуть её текст
async def mark_task_complete(task_id: int, user_id: int):
    print(f"Попытка отметить задачу с ID {task_id} выполненной для пользователя {user_id}")  # Логирование
    async with async_session_maker() as session:
        result = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id, Task.completed == False)
        )
        task = result.scalar_one_or_none()
        if not task:
            print(f"Задача с ID {task_id} не найдена или уже выполнена.")  # Логирование
            return None

        task.completed = True
        await session.commit()

        # Начисляем очки пользователю
        await session.execute(
            update(User).where(User.id == user_id).values(
                score=User.score + 10
            )
        )
        await session.commit()
        print(f"Задача с ID {task_id} выполнена. Очки добавлены пользователю {user_id}.")  # Логирование

        return task.text

# Получение списка лидеров
async def get_leaderboard_data(limit: int = 10):
    print(f"Запрос на получение таблицы лидеров с лимитом {limit}")  # Логирование
    async with async_session_maker() as session:
        result = await session.execute(
            select(User.username, User.score)
            .order_by(User.score.desc())
            .limit(limit)
        )
        leaderboard = [dict(row._mapping) for row in result.fetchall()]
        print(f"Получено {len(leaderboard)} записей для таблицы лидеров.")  # Логирование
        return leaderboard

# reactions
async def select_reaction(session, user_id, message_id):
    result = await session.execute(
        select(Reaction).where(
            Reaction.user_id == user_id,
            Reaction.message_id == message_id
        )
    )
    return result.scalar_one_or_none()

async def select_emojis_for_message(session, message_id):
    result = await session.execute(
        select(Reaction.emoji).where(Reaction.message_id == message_id)
    )
    return [row[0] for row in result.all()]