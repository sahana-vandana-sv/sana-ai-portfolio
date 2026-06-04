"""Register Telegram webhook. Run once after deploy.
Usage: python -m bot.register_webhook
"""

import asyncio
import os
from telegram import Bot


async def register():
    base_url = os.environ["WEBHOOK_BASE_URL"].rstrip("/")
    webhook_url = f"{base_url}/webhook/telegram"
    bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
    await bot.set_webhook(url=webhook_url)
    info = await bot.get_webhook_info()
    print(f"Webhook set: {info.url}")
    print(f"Pending updates: {info.pending_update_count}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(register())
