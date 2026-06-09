"""
Short-term conversation memory backed by Redis.

- Key per user: "conversation:{user_id}"
- Stores the last MAX_MESSAGES messages as a Redis list (left = oldest, right = newest)
- Each entry is a JSON-encoded dict: {"role": "user"|"assistant", "content": str}
- TTL refreshed to 2 hours on every read or write
"""
import json
import os
from typing import Optional

import redis

MAX_MESSAGES = 10
TTL_SECONDS = 2 * 60 * 60  # 2 hours


def _get_client() -> redis.Redis:
    url = os.getenv("REDIS_URL", "redis://localhost:6379")
    return redis.from_url(url, decode_responses=True)


def _key(user_id: str) -> str:
    return f"conversation:{user_id}"


def add_message(user_id: str, role: str, content: str, client: Optional[redis.Redis] = None) -> None:
    """
    Append a message to the conversation history for user_id.
    Trims to the last MAX_MESSAGES entries and refreshes the TTL.
    """
    r = client or _get_client()
    k = _key(user_id)
    payload = json.dumps({"role": role, "content": content})
    r.rpush(k, payload)
    r.ltrim(k, -MAX_MESSAGES, -1)
    r.expire(k, TTL_SECONDS)


def get_history(user_id: str, client: Optional[redis.Redis] = None) -> list[dict]:
    """
    Return the conversation history for user_id as a list of dicts.
    Refreshes the TTL. Returns [] if no history exists.
    """
    r = client or _get_client()
    k = _key(user_id)
    raw = r.lrange(k, 0, -1)
    if raw:
        r.expire(k, TTL_SECONDS)
    return [json.loads(entry) for entry in raw]


def clear_history(user_id: str, client: Optional[redis.Redis] = None) -> None:
    """Delete the conversation history for user_id."""
    r = client or _get_client()
    r.delete(_key(user_id))
