"""
Session 3 tests — short-term Redis memory.
Run: pytest tests/test_memory.py -v
No live Redis required — uses fakeredis.
"""
import pytest
import fakeredis
from memory.short_term import add_message, get_history, clear_history, MAX_MESSAGES


@pytest.fixture()
def r():
    """A fresh fakeredis client for each test."""
    return fakeredis.FakeRedis(decode_responses=True)


# ── Basic read / write ────────────────────────────────────────────────────────

def test_empty_history(r):
    assert get_history("user1", client=r) == []


def test_add_single_message(r):
    add_message("user1", "user", "Hello", client=r)
    history = get_history("user1", client=r)
    assert len(history) == 1
    assert history[0] == {"role": "user", "content": "Hello"}


def test_add_multiple_messages(r):
    add_message("user1", "user", "Hi", client=r)
    add_message("user1", "assistant", "Hello there!", client=r)
    history = get_history("user1", client=r)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_messages_are_ordered(r):
    for i in range(3):
        add_message("user1", "user", f"msg{i}", client=r)
    history = get_history("user1", client=r)
    assert [m["content"] for m in history] == ["msg0", "msg1", "msg2"]


# ── MAX_MESSAGES trimming ─────────────────────────────────────────────────────

def test_trims_to_max_messages(r):
    for i in range(MAX_MESSAGES + 5):
        add_message("user1", "user", f"msg{i}", client=r)
    history = get_history("user1", client=r)
    assert len(history) == MAX_MESSAGES


def test_trim_keeps_newest_messages(r):
    for i in range(MAX_MESSAGES + 3):
        add_message("user1", "user", f"msg{i}", client=r)
    history = get_history("user1", client=r)
    # The oldest entries should have been dropped
    assert history[0]["content"] == "msg3"
    assert history[-1]["content"] == f"msg{MAX_MESSAGES + 2}"


# ── TTL ───────────────────────────────────────────────────────────────────────

def test_ttl_set_on_add(r):
    add_message("user1", "user", "Hello", client=r)
    ttl = r.ttl("conversation:user1")
    assert ttl > 0


def test_ttl_refreshed_on_get(r):
    add_message("user1", "user", "Hello", client=r)
    # Manually reduce TTL
    r.expire("conversation:user1", 10)
    get_history("user1", client=r)
    ttl = r.ttl("conversation:user1")
    # TTL should have been reset to ~7200, well above 10
    assert ttl > 100


# ── Isolation between users ───────────────────────────────────────────────────

def test_users_are_isolated(r):
    add_message("user1", "user", "Hello from user1", client=r)
    add_message("user2", "user", "Hello from user2", client=r)
    assert get_history("user1", client=r)[0]["content"] == "Hello from user1"
    assert get_history("user2", client=r)[0]["content"] == "Hello from user2"


# ── clear_history ─────────────────────────────────────────────────────────────

def test_clear_history(r):
    add_message("user1", "user", "Hello", client=r)
    clear_history("user1", client=r)
    assert get_history("user1", client=r) == []


def test_clear_nonexistent_history_is_safe(r):
    clear_history("nobody", client=r)   # should not raise
