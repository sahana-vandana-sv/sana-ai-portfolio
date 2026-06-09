"""
Session 4 tests — Supabase task tool.
Run: pytest tests/test_tools.py -v
No live Supabase connection required — Supabase client is mocked.
"""
import uuid
from unittest.mock import MagicMock, patch
import pytest

from tools.task_store import create_task, get_task, list_tasks, update_task, delete_task


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_task(overrides: dict | None = None) -> dict:
    """Return a fake task row as Supabase would."""
    base = {
        "id": str(uuid.uuid4()),
        "user_id": "user_test",
        "title": "Buy milk",
        "description": None,
        "status": "pending",
        "due_date": None,
        "created_at": "2026-06-09T10:00:00+00:00",
        "updated_at": "2026-06-09T10:00:00+00:00",
    }
    if overrides:
        base.update(overrides)
    return base


def _mock_client(rows: list[dict]) -> MagicMock:
    """Build a mock Supabase client whose .execute() returns the given rows."""
    mock_resp = MagicMock()
    mock_resp.data = rows

    mock_query = MagicMock()
    mock_query.execute.return_value = mock_resp
    # Chain: .select().eq().order() all return the same mock_query
    mock_query.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.insert.return_value = mock_query
    mock_query.update.return_value = mock_query
    mock_query.delete.return_value = mock_query

    mock_client = MagicMock()
    mock_client.table.return_value = mock_query
    return mock_client


# ── create_task ───────────────────────────────────────────────────────────────

def test_create_task_returns_row():
    task = _make_task()
    client = _mock_client([task])
    result = create_task("user_test", "Buy milk", client=client)
    assert result["title"] == "Buy milk"
    assert result["status"] == "pending"
    assert result["user_id"] == "user_test"


def test_create_task_with_description_and_due_date():
    task = _make_task({"description": "From the corner shop", "due_date": "2026-06-10T09:00:00+00:00"})
    client = _mock_client([task])
    result = create_task(
        "user_test",
        "Buy milk",
        description="From the corner shop",
        due_date="2026-06-10T09:00:00+00:00",
        client=client,
    )
    assert result["description"] == "From the corner shop"
    assert result["due_date"] == "2026-06-10T09:00:00+00:00"


def test_create_task_inserts_into_correct_table():
    task = _make_task()
    client = _mock_client([task])
    create_task("user_test", "Buy milk", client=client)
    client.table.assert_called_with("tasks")


# ── get_task ──────────────────────────────────────────────────────────────────

def test_get_task_found():
    task = _make_task()
    client = _mock_client([task])
    result = get_task(task["id"], client=client)
    assert result["id"] == task["id"]


def test_get_task_not_found():
    client = _mock_client([])
    result = get_task(str(uuid.uuid4()), client=client)
    assert result is None


# ── list_tasks ────────────────────────────────────────────────────────────────

def test_list_tasks_returns_all_for_user():
    tasks = [_make_task({"title": f"Task {i}"}) for i in range(3)]
    client = _mock_client(tasks)
    result = list_tasks("user_test", client=client)
    assert len(result) == 3


def test_list_tasks_empty():
    client = _mock_client([])
    result = list_tasks("user_test", client=client)
    assert result == []


def test_list_tasks_with_status_filter():
    done_task = _make_task({"status": "done"})
    client = _mock_client([done_task])
    result = list_tasks("user_test", status="done", client=client)
    assert result[0]["status"] == "done"
    # Verify .eq was called with status filter
    client.table.return_value.eq.assert_any_call("status", "done")


# ── update_task ───────────────────────────────────────────────────────────────

def test_update_task_status():
    updated = _make_task({"status": "done"})
    client = _mock_client([updated])
    result = update_task(updated["id"], status="done", client=client)
    assert result["status"] == "done"


def test_update_task_title():
    updated = _make_task({"title": "Buy oat milk"})
    client = _mock_client([updated])
    result = update_task(updated["id"], title="Buy oat milk", client=client)
    assert result["title"] == "Buy oat milk"


def test_update_task_not_found():
    client = _mock_client([])
    result = update_task(str(uuid.uuid4()), status="done", client=client)
    assert result is None


# ── delete_task ───────────────────────────────────────────────────────────────

def test_delete_task_success():
    task = _make_task()
    client = _mock_client([task])
    result = delete_task(task["id"], client=client)
    assert result is True


def test_delete_task_not_found():
    client = _mock_client([])
    result = delete_task(str(uuid.uuid4()), client=client)
    assert result is False
