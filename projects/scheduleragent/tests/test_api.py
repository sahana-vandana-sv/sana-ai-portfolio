"""
Session 1 tests.  Run: pytest tests/test_api.py -v

test_health + test_webhook  → no network needed
test_claude_endpoint        → live Anthropic call (needs real key in .env)
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "scheduleragent"}


def test_webhook_telegram():
    r = client.post("/webhook/telegram", json={"message": {"text": "hello"}})
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_claude_endpoint():
    """Live API call — will fail if ANTHROPIC_API_KEY is still a placeholder."""
    r = client.get("/test-claude")
    assert r.status_code == 200, f"Got {r.status_code}: {r.text}"
    data = r.json()
    assert "response" in data and len(data["response"]) > 0
    print(f"\n  Claude said: {data['response']}")
