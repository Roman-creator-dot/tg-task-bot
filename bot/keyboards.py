from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить задачу")],
            [KeyboardButton(text="📋 Мои задачи")],
            [KeyboardButton(text="📊 топ")],
        ],
        resize_keyboard=True
    )

# Кнопки под задачами
def tasks_inline_kb(tasks):
    buttons = [
        [InlineKeyboardButton(text=task.text, callback_data=f"complete:{task.id}")]
        for task in tasks
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
