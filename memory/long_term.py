"""Long-term memory is backed by Supabase Postgres + pgvector.
Actual read/write logic lives in tools/memory_store.py and tools/notes_db.py.
This module exposes a unified interface for retrieving all context about a user.
"""

from tools.memory_store import get_preferences
from tools.notes_db import search_notes


async def get_user_context(user_id: str, query: str = "") -> dict:
    preferences = await get_preferences(user_id)
    notes = await search_notes(user_id, query) if query else []
    return {"preferences": preferences, "relevant_notes": notes}
