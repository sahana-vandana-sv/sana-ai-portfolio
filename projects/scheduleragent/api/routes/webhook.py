import structlog
from fastapi import APIRouter, Request

log = structlog.get_logger()
router = APIRouter()


# SESSION 1: stub — just logs the incoming body and returns ok.
# No agents, no Telegram parsing, no graph. That comes in Session 10.
@router.post("/telegram")
async def telegram_webhook(request: Request):
    body = await request.json()
    log.info("webhook_received", body=body)
    return {"ok": True}
