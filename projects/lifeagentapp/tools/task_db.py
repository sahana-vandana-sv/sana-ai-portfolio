import os
import uuid
from datetime import datetime

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


async def create_task(user_id: str, title: str, due_date: str | None = None) -> dict:
    task = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "due_date": due_date,
        "completed": False,
        "created_at": datetime.utcnow().isoformat(),
    }
    result = get_client().table("tasks").insert(task).execute()
    return result.data[0] if result.data else task


async def list_tasks(user_id: str, completed: bool = False) -> list[dict]:
    result = (
        get_client()
        .table("tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("completed", completed)
        .order("created_at", desc=False)
        .execute()
    )
    return result.data or []


async def complete_task(task_id: str) -> dict:
    result = (
        get_client()
        .table("tasks")
        .update({"completed": True})
        .eq("id", task_id)
        .execute()
    )
    return result.data[0] if result.data else {}
