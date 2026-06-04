import structlog
from fastapi import APIRouter, Request, HTTPException
from telegram import Update

from bot.telegram_handler import process_update

log = structlog.get_logger()
router = APIRouter()


@router.post("/telegram")
async def telegram_webhook(request: Request):
    """Receive Telegram webhook updates and dispatch to the agent pipeline."""
    try:
        data = await request.json()
        update = Update.de_json(data, bot=None)
        await process_update(update)
        return {"ok": True}
    except Exception as e:
        log.error("webhook_error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal error")
