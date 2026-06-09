"""
Task CRUD operations backed by Supabase.

Table: tasks
  id          uuid (pk, auto)
  user_id     text
  title       text
  description text (nullable)
  status      text  — 'pending' | 'in_progress' | 'done'
  due_date    timestamptz (nullable, ISO-8601 string)
  created_at  timestamptz (auto)
  updated_at  timestamptz (auto)
"""
from __future__ import annotations

import os
from typing import Optional

from supabase import create_client, Client


def _get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)


# ── Create ────────────────────────────────────────────────────────────────────

def create_task(
    user_id: str,
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    *,
    client: Client | None = None,
) -> dict:
    """
    Insert a new task and return the created row.

    Args:
        user_id:     Owner of the task.
        title:       Short title (required).
        description: Optional longer description.
        due_date:    Optional ISO-8601 datetime string.
        client:      Inject a Supabase client (used in tests).
    """
    c = client or _get_client()
    payload: dict = {"user_id": user_id, "title": title, "status": "pending"}
    if description is not None:
        payload["description"] = description
    if due_date is not None:
        payload["due_date"] = due_date

    response = c.table("tasks").insert(payload).execute()
    return response.data[0]


# ── Read ──────────────────────────────────────────────────────────────────────

def get_task(task_id: str, *, client: Client | None = None) -> dict | None:
    """Return a single task by id, or None if not found."""
    c = client or _get_client()
    response = c.table("tasks").select("*").eq("id", task_id).execute()
    return response.data[0] if response.data else None


def list_tasks(
    user_id: str,
    status: str | None = None,
    *,
    client: Client | None = None,
) -> list[dict]:
    """
    Return all tasks for user_id, optionally filtered by status.
    Results are ordered by created_at ascending.
    """
    c = client or _get_client()
    query = c.table("tasks").select("*").eq("user_id", user_id)
    if status is not None:
        query = query.eq("status", status)
    response = query.order("created_at").execute()
    return response.data


# ── Update ────────────────────────────────────────────────────────────────────

def update_task(
    task_id: str,
    *,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    due_date: str | None = None,
    client: Client | None = None,
) -> dict | None:
    """
    Update one or more fields on a task. Returns the updated row, or None
    if the task was not found.
    """
    c = client or _get_client()
    payload: dict = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if status is not None:
        payload["status"] = status
    if due_date is not None:
        payload["due_date"] = due_date

    if not payload:
        return get_task(task_id, client=c)

    response = c.table("tasks").update(payload).eq("id", task_id).execute()
    return response.data[0] if response.data else None


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_task(task_id: str, *, client: Client | None = None) -> bool:
    """Delete a task by id. Returns True if a row was deleted."""
    c = client or _get_client()
    response = c.table("tasks").delete().eq("id", task_id).execute()
    return len(response.data) > 0
