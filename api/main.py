from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.webhook import router as webhook_router
from api.routes.health import router as health_router

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("LifeAgent starting up")
    yield
    log.info("LifeAgent shutting down")


app = FastAPI(
    title="LifeAgent",
    description="Personal Life OS Agent — chat with your life via Telegram",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(webhook_router, prefix="/webhook")
