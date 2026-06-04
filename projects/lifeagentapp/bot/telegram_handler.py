import os

import structlog
from telegram import Bot, Update, Message

from agents.graph import run_agent
from memory.short_term import get_context, add_to_context

log = structlog.get_logger()

_bot: Bot | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
    return _bot


async def process_update(update: Update) -> None:
    """Entry point for all Telegram updates."""
    if not update.message or not update.message.text:
        return

    message: Message = update.message
    chat_id = str(message.chat_id)
    user_id = str(message.from_user.id) if message.from_user else chat_id
    text = message.text.strip()

    log.info("message_received", chat_id=chat_id, text=text[:80])

    short_term = await get_context(chat_id)

    result = await run_agent(
        user_id=user_id,
        chat_id=chat_id,
        message=text,
        short_term_context=short_term,
    )

    await add_to_context(chat_id, role="user", content=text)
    await add_to_context(chat_id, role="assistant", content=result["reply"])

    bot = get_bot()
    await bot.send_message(chat_id=chat_id, text=result["reply"])
