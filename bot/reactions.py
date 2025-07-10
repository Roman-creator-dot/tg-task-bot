from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from db.base import async_session_maker
from bot.reaction_utils import get_reaction, get_all_emojis_for_message
from db.models import Reaction, User
import os

SCORE_REACTION = int(os.getenv("SCORE_REACTION", 1))  # Очки за реакцию

router = Router()

REACTIONS = {
    "👍": 1,
    "🔥": 2,
    "💡": 3
}


def build_reaction_keyboard_with_counts(counts: dict[str, int]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=f"{emoji} {counts.get(emoji, 0)}",
            callback_data=f"react:{emoji}"
        )
        for emoji in REACTIONS.keys()
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


@router.callback_query(F.data.startswith("react:"))
async def handle_reaction_callback(callback: types.CallbackQuery):
    emoji = callback.data.split(":")[1]
    user_id = callback.from_user.id
    message_id = callback.message.message_id

    async with async_session_maker() as session:
        user = await session.get(User, user_id)
        if not user:
            await callback.answer("Вы не зарегистрированы.", show_alert=True)
            return

        existing_reaction = await get_reaction(session, user_id, message_id)

        if existing_reaction:
            if existing_reaction.emoji == emoji:
                await session.delete(existing_reaction)
                user.score -= SCORE_REACTION
                await callback.answer("Реакция удалена")
            else:
                user.score -= SCORE_REACTION
                existing_reaction.emoji = emoji
                user.score += SCORE_REACTION
                await callback.answer(f"Реакция изменена на {emoji}")
        else:
            new_reaction = Reaction(user_id=user_id, message_id=message_id, emoji=emoji)
            session.add(new_reaction)
            user.score += SCORE_REACTION
            await callback.answer(f"Вы выбрали {emoji}")

        await session.commit()

        all_emojis = await get_all_emojis_for_message(session, message_id)
        counts = {emoji: all_emojis.count(emoji) for emoji in REACTIONS.keys()}

        await callback.message.edit_reply_markup(
            reply_markup=build_reaction_keyboard_with_counts(counts)
        )


# Используется другими модулями для публикации сообщений с реакциями
async def send_message_with_reactions(bot, chat_id: int, text: str):
    message = await bot.send_message(chat_id, text, reply_markup=build_reaction_keyboard_with_counts({}))
    return message.message_id