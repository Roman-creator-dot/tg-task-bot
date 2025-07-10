# bot/reaction_utils.py
from db.queries import select_reaction, select_emojis_for_message

async def get_reaction(session, user_id, message_id):
    return await select_reaction(session, user_id, message_id)

async def get_all_emojis_for_message(session, message_id):
    return await select_emojis_for_message(session, message_id)
