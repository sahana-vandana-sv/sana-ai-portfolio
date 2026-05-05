"""
Day 1 tests.
Run: pytest tests/test_day1.py -v
"""
import os
import pytest
import pandas as pd
from fastapi.testclient import TestClient

os.environ["DB_PATH"] = "data/test.db"

from app.main import app
import app.db as db
from app.db import insert_transaction, get_transaction_count, get_all_transactions


@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    """Each test gets a clean database."""
    test_db = str(tmp_path / "test.db")
    db.DB_PATH = test_db
    db.init_db()
    yield
    db.DB_PATH = "data/test.db"


@pytest.fixture()
def client():
    return TestClient(app)


class TestDatabase:
    def test_init_creates_table(self):
        assert get_transaction_count() == 0

    def test_insert_transaction(self):
        txn = {
            "txn_id": "TXN001",
            "date": "2024-04-01",
            "description": "TESCO LONDON",
            "amount": 42.35,
            "currency": "GBP",
            "merchant": "Tesco",
            "account_id": "ACC001",
        }
        inserted = insert_transaction(txn)
        assert inserted is True
        assert get_transaction_count() == 1

    def test_duplicate_is_ignored(self):
        txn = {
            "txn_id": "TXN001",
            "date": "2024-04-01",
            "description": "TESCO LONDON",
            "amount": 42.35,
            "currency": "GBP",
            "merchant": "Tesco",
            "account_id": "ACC001",
        }
        insert_transaction(txn)
        second = insert_transaction(txn)
        assert second is False
        assert get_transaction_count() == 1

    def test_get_all_returns_dicts(self):
        txn = {
            "txn_id": "TXN001", "date": "2024-04-01",
            "description": "TESCO", "amount": 10.0,
            "currency": "GBP", "merchant": "Tesco", "account_id": "ACC001",
        }
        insert_transaction(txn)
        rows = get_all_transactions()
        assert isinstance(rows, list)
        assert isinstance(rows[0], dict)
        assert rows[0]["txn_id"] == "TXN001"


class TestSeedCSV:
    def test_csv_has_50_rows(self):
        df = pd.read_csv("data/seed_transactions.csv")
        assert len(df) == 50

    def test_no_duplicate_txn_ids(self):
        df = pd.read_csv("data/seed_transactions.csv")
        assert df["txn_id"].is_unique

    def test_no_nulls_in_required_columns(self):
        df = pd.read_csv("data/seed_transactions.csv")
        for col in ["txn_id", "date", "description", "amount"]:
            assert df[col].notna().all(), f"Nulls in {col}"


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_shows_transaction_count(self, client):
        response = client.get("/health")
        assert "transactions_in_db" in response.json()

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200