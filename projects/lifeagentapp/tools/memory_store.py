import os
import uuid
from datetime import datetime
from typing import Any

import structlog
from supabase import create_client, Client

log = structlog.get_logger()

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"],
        )
    return _client


async def store_preference(
    user_id: str, content: str, entities: dict[str, Any] = {}
) -> dict:
    pref = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "content": content,
        "entities": entities,
        "created_at": datetime.utcnow().isoformat(),
    }
    result = get_client().table("memory").insert(pref).execute()
    return result.data[0] if result.data else pref


async def get_preferences(user_id: str) -> list[dict]:
    result = (
        get_client()
        .table("memory")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(20)
        .execute()
    )
    return result.data or []
