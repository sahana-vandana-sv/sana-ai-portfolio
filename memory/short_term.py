import json
import os

import redis.asyncio as aioredis

_redis: aioredis.Redis | None = None
MAX_CONTEXT_MESSAGES = 10
TTL_SECONDS = 60 * 60 * 2  # 2 hours


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
    return _redis


def _key(chat_id: str) -> str:
    return f"lifeagent:context:{chat_id}"


async def get_context(chat_id: str) -> list[dict]:
    r = get_redis()
    raw = await r.get(_key(chat_id))
    if not raw:
        return []
    return json.loads(raw)


async def add_to_context(chat_id: str, role: str, content: str) -> None:
    r = get_redis()
    key = _key(chat_id)
    messages = await get_context(chat_id)
    messages.append({"role": role, "content": content})
    messages = messages[-MAX_CONTEXT_MESSAGES:]
    await r.setex(key, TTL_SECONDS, json.dumps(messages))


async def clear_context(chat_id: str) -> None:
    r = get_redis()
    await r.delete(_key(chat_id))
