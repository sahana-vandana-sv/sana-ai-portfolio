"""
Day 4 tests — anomaly detection service + endpoints.
Run: pytest tests/test_day4.py -v
"""
import os
import pytest
from fastapi.testclient import TestClient

os.environ["DB_PATH"] = "data/test.db"
os.environ["CLASSIFY_ON_INGEST"] = "false"
os.environ["ANTHROPIC_API_KEY"] = "test-key"

from app.main import app
import app.db as db
import app.api.transactions as txn_module
from app.db import insert_transaction, update_category, update_anomaly, get_anomalies
from app.services.anomaly import  detect_anomaly, detect_anomalies_bulk, THRESHOLD


@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    test_db = str(tmp_path / "test.db")
    db.DB_PATH = test_db
    txn_module.CLASSIFY_ON_INGEST = False
    db.init_db()
    yield
    db.DB_PATH = "data/test.db"


@pytest.fixture()
def client():
    return TestClient(app)


def make_txn(txn_id, amount, category=None):
    t = {
        "txn_id": txn_id, "date": "2024-04-01",
        "description": f"TXN {txn_id}", "amount": amount,
        "currency": "GBP", "merchant": None, "account_id": None,
    }
    insert_transaction(t)
    if category:
        update_category(txn_id, category, 0.95)
    return {**t, "category": category}


# ── Z-score unit tests ────────────────────────────────────────────────────────




# ── detect_anomaly unit tests ─────────────────────────────────────────────────

class TestDetectAnomaly:
    def test_normal_txn_not_flagged(self):
        txn = {"txn_id": "T1", "amount": 10.0}
        peers = [
            {"txn_id": "T2", "amount": 9.0},
            {"txn_id": "T3", "amount": 11.0},
            {"txn_id": "T4", "amount": 10.5},
        ]
        result = detect_anomaly(txn, peers)
        assert result["is_anomaly"] is False

    def test_spike_is_flagged(self):
        txn = {"txn_id": "T1", "amount": 500.0}
        peers = [
            {"txn_id": "T2", "amount": 10.0},
            {"txn_id": "T3", "amount": 10.0},
            {"txn_id": "T4", "amount": 10.0},
            {"txn_id": "T5", "amount": 10.0},
        ]
        result = detect_anomaly(txn, peers)
        assert result["is_anomaly"] is True

    def test_insufficient_data_not_flagged(self):
        txn = {"txn_id": "T1", "amount": 500.0}
        peers = [{"txn_id": "T2", "amount": 10.0}]  # only 1 peer, below MIN_SAMPLES
        result = detect_anomaly(txn, peers)
        assert result["is_anomaly"] is False

    def test_result_has_required_fields(self):
        txn = {"txn_id": "T1", "amount": 10.0}
        peers = [
            {"txn_id": "T2", "amount": 9.0},
            {"txn_id": "T3", "amount": 11.0},
            {"txn_id": "T4", "amount": 10.0},
        ]
        result = detect_anomaly(txn, peers)
        for field in ["is_anomaly", "zscore", "category_mean", "category_std", "reason"]:
            assert field in result

    def test_txn_excluded_from_its_own_peers(self):
        # The transaction itself should not be included in the peer amounts
        txn = {"txn_id": "T1", "amount": 500.0}
        peers = [
            {"txn_id": "T1", "amount": 500.0},  # same txn — should be excluded
            {"txn_id": "T2", "amount": 10.0},
            {"txn_id": "T3", "amount": 10.0},
            {"txn_id": "T4", "amount": 10.0},
        ]
        result = detect_anomaly(txn, peers)
        assert result["is_anomaly"] is True  # would be False if T1 included itself


# ── detect_anomalies_bulk ─────────────────────────────────────────────────────

class TestBulkDetection:
    def test_bulk_returns_same_count(self):
        txns = [
            {"txn_id": f"T{i}", "amount": 10.0, "category": "groceries"}
            for i in range(5)
        ]
        results = detect_anomalies_bulk(txns)
        assert len(results) == 5

    def test_bulk_adds_anomaly_detail(self):
        txns = [
            {"txn_id": f"T{i}", "amount": 10.0, "category": "groceries"}
            for i in range(5)
        ]
        results = detect_anomalies_bulk(txns)
        assert all("anomaly_detail" in r for r in results)

    def test_bulk_spike_detected(self):
        txns = [
            {"txn_id": "T1", "amount": 10.0, "category": "groceries"},
            {"txn_id": "T2", "amount": 10.0, "category": "groceries"},
            {"txn_id": "T3", "amount": 10.0, "category": "groceries"},
            {"txn_id": "T4", "amount": 10.0, "category": "groceries"},
            {"txn_id": "T5", "amount": 500.0, "category": "groceries"},  # spike
        ]
        results = detect_anomalies_bulk(txns)
        spike = next(r for r in results if r["txn_id"] == "T5")
        assert spike["anomaly_detail"]["is_anomaly"] is True

    def test_bulk_groups_by_category(self):
        # A high amount in one category should not affect another
        txns = [
            {"txn_id": "T1", "amount": 10.0, "category": "groceries"},
            {"txn_id": "T2", "amount": 10.0, "category": "groceries"},
            {"txn_id": "T3", "amount": 10.0, "category": "groceries"},
            {"txn_id": "T4", "amount": 10.0, "category": "groceries"},
            {"txn_id": "T5", "amount": 500.0, "category": "transport"},  # high but only txn in category
        ]
        results = detect_anomalies_bulk(txns)
        transport = next(r for r in results if r["txn_id"] == "T5")
        # Only 1 transport txn — insufficient data, should not be flagged
        assert transport["anomaly_detail"]["is_anomaly"] is False


# ── DB functions ──────────────────────────────────────────────────────────────

class TestAnomalyDB:
    def test_update_anomaly_sets_flag(self):
        make_txn("T1", 10.0, "groceries")
        update_anomaly("T1", True)
        anomalies = get_anomalies()
        assert len(anomalies) == 1
        assert anomalies[0]["txn_id"] == "T1"

    def test_update_anomaly_clears_flag(self):
        make_txn("T1", 10.0, "groceries")
        update_anomaly("T1", True)
        update_anomaly("T1", False)
        assert len(get_anomalies()) == 0

    def test_get_anomalies_returns_only_flagged(self):
        make_txn("T1", 10.0, "groceries")
        make_txn("T2", 10.0, "groceries")
        update_anomaly("T1", True)
        anomalies = get_anomalies()
        assert len(anomalies) == 1
        assert anomalies[0]["txn_id"] == "T1"


# ── API endpoints ─────────────────────────────────────────────────────────────

class TestDetectEndpoint:
    def test_detect_with_no_categorised_rows(self, client):
        response = client.post("/transactions/detect")
        assert response.status_code == 200
        assert "No categorised transactions" in response.json()["message"]

    def test_detect_flags_spike(self, client):
        # Seed 4 normal groceries + 1 spike
        for i in range(1, 5):
            make_txn(f"T{i}", 10.0, "groceries")
        make_txn("T5", 500.0, "groceries")

        response = client.post("/transactions/detect")
        assert response.status_code == 200
        assert response.json()["anomalies_found"] >= 1

    def test_anomalies_endpoint_returns_flagged(self, client):
        make_txn("T1", 10.0, "groceries")
        update_anomaly("T1", True)
        response = client.get("/transactions/anomalies")
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_anomalies_endpoint_empty(self, client):
        response = client.get("/transactions/anomalies")
        assert response.status_code == 200
        assert response.json()["total"] == 0