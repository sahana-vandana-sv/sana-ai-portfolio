"""
SESSION 1 — api/main.py
What this file does right now:
  - Loads .env so every module can read os.environ
  - Creates the FastAPI app with CORS
  - Mounts /health and /webhook/telegram (stub)
  - Adds /test-claude to prove the Anthropic key works

Nothing about agents, Redis, Supabase, or Telegram exists yet.
Each future session will import new routers and wire them in here.
"""
import os
from contextlib import asynccontextmanager

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)  # must be before any os.getenv() calls elsewhere

from api.routes.health import router as health_router
from api.routes.webhook import router as webhook_router

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    key_preview = (os.getenv("ANTHROPIC_API_KEY") or "")[:8] or "NOT SET"
    log.info("scheduleragent starting", anthropic_key_prefix=key_preview)
    yield
    log.info("scheduleragent shutting down")


app = FastAPI(title="SchedulerAgent", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(webhook_router, prefix="/webhook")


# ── SESSION 1 ONLY ────────────────────────────────────────────────────────────
# This endpoint exists purely to confirm your key + SDK work before any agents
# are built. You will delete or replace it in a later session.
@app.get("/test-claude")
async def test_claude():
    """Hit this with curl to prove end-to-end: env → SDK → Claude → response."""
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=64,
        messages=[{"role": "user", "content": "Say hello in one sentence."}],
    )
    response_text = message.content[0].text
    log.info("test_claude_ok", response=response_text)
    return {"response": response_text}
