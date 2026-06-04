import os
import uuid
from datetime import datetime
from typing import Any

import structlog
from supabase import create_client, Client

log = structlog.get_logger()

_client: Client | None = None

EMBEDDING_MODEL = "text-embedding-3-small"  # via OpenAI or local sentence-transformers


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"],
        )
    return _client


def _embed(text: str) -> list[float]:
    """Generate embedding using sentence-transformers (local, no extra API cost)."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model.encode(text).tolist()


async def store_note(user_id: str, content: str, entities: dict[str, Any] = {}) -> dict:
    embedding = _embed(content)
    note = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "content": content,
        "entities": entities,
        "embedding": embedding,
        "created_at": datetime.utcnow().isoformat(),
    }
    result = get_client().table("notes").insert(note).execute()
    return result.data[0] if result.data else note


async def search_notes(user_id: str, query: str, limit: int = 5) -> list[dict]:
    embedding = _embed(query)
    # pgvector cosine similarity search via RPC
    result = get_client().rpc(
        "match_notes",
        {
            "query_embedding": embedding,
            "match_user_id": user_id,
            "match_count": limit,
        },
    ).execute()
    return result.data or []
