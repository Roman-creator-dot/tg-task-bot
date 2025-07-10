# Файл: db/models.py
# Определение таблиц User и Task через SQLAlchemy ORM

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,BigInteger
from sqlalchemy.orm import DeclarativeBase, relationship

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Пользователь
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Telegram ID
    username = Column(String, nullable=False)
    score = Column(Integer, default=0)

    # связь с задачами (один ко многим)
    tasks = relationship("Task", back_populates="user")

# Задача
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    text = Column(String, nullable=False)
    completed = Column(Boolean, default=False)

    # связь с пользователем (многие к одному)
    user = relationship("User", back_populates="tasks")

class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True)
    message_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    emoji = Column(String, nullable=False)

    user = relationship("User")