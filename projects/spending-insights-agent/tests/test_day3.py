"""
Day 3 tests — LLM classifier (mocked) + classification wired into ingest.
Run: pytest tests/test_day3.py -v

Claude API is always mocked — tests never make real API calls.
"""
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Disable real classification in the API layer
os.environ["DB_PATH"] = "data/test.db"
os.environ["CLASSIFY_ON_INGEST"] = "false"

from app.main import app
import app.db as db
from app.db import insert_transaction, get_uncategorised, update_category
from app.services.classifier import classify_transaction, ClassificationError, CATEGORIES


@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    test_db = str(tmp_path / "test.db")
    db.DB_PATH = test_db
    db.init_db()
    yield
    db.DB_PATH = "data/test.db"


@pytest.fixture()
def client():
    return TestClient(app)


def make_mock_response(category: str, confidence: float = 0.95) -> MagicMock:
    """Build a mock that looks like an Anthropic API response."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = json.dumps({
        "category": category,
        "confidence": confidence,
        "reasoning": f"Test reasoning for {category}.",
    })
    return mock_response


# ── Classifier unit tests ─────────────────────────────────────────────────────

class TestClassifier:
    def test_returns_valid_category(self):
        with patch("app.services.classifier.anthropic.Anthropic") as mock_client:
            mock_client.return_value.messages.create.return_value = make_mock_response("groceries")
            result = classify_transaction("TESCO SUPERSTORE", 42.35)
        assert result["category"] == "groceries"

    def test_returns_confidence_as_float(self):
        with patch("app.services.classifier.anthropic.Anthropic") as mock_client:
            mock_client.return_value.messages.create.return_value = make_mock_response("transport", 0.88)
            result = classify_transaction("TFL TRAVEL CHARGE", 6.40)
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_returns_reasoning_string(self):
        with patch("app.services.classifier.anthropic.Anthropic") as mock_client:
            mock_client.return_value.messages.create.return_value = make_mock_response("subscriptions")
            result = classify_transaction("NETFLIX.COM", 17.99)
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0

    def test_unknown_category_falls_back_to_other(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = json.dumps({
            "category": "this_is_not_real",
            "confidence": 0.5,
            "reasoning": "Unknown.",
        })
        with patch("app.services.classifier.anthropic.Anthropic") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_response
            result = classify_transaction("MYSTERY SHOP", 10.0)
        assert result["category"] == "other"
        assert result["confidence"] == 0.0

    def test_api_error_raises_classification_error(self):
        import anthropic as anthropic_lib
        with patch("app.services.classifier.anthropic.Anthropic") as mock_client:
            mock_client.return_value.messages.create.side_effect = anthropic_lib.APIError(
                message="rate limit", request=MagicMock(), body={}
            )
            with pytest.raises(ClassificationError):
                classify_transaction("TESCO", 42.35)

    def test_non_json_response_raises_classification_error(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Sorry, I cannot classify this."
        with patch("app.services.classifier.anthropic.Anthropic") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_response
            with pytest.raises(ClassificationError):
                classify_transaction("TESCO", 42.35)

    def test_all_seed_categories_are_valid(self):
        """Sanity check: every category in CATEGORIES is a non-empty string."""
        assert len(CATEGORIES) > 0
        for cat in CATEGORIES:
            assert isinstance(cat, str) and len(cat) > 0


# ── DB: update_category and get_uncategorised ─────────────────────────────────

class TestCategoryDB:
    def test_update_category_persists(self):
        txn = {
            "txn_id": "TXN001", "date": "2024-04-01",
            "description": "TESCO", "amount": 42.35,
            "currency": "GBP", "merchant": "Tesco", "account_id": "ACC001",
        }
        insert_transaction(txn)
        update_category("TXN001", "groceries", 0.97)

        from app.db import get_all_transactions
        rows = get_all_transactions()
        assert rows[0]["category"] == "groceries"

    def test_get_uncategorised_returns_null_category_rows(self):
        for i in range(3):
            insert_transaction({
                "txn_id": f"TXN00{i}", "date": "2024-04-01",
                "description": "SHOP", "amount": 10.0,
                "currency": "GBP", "merchant": None, "account_id": None,
            })
        assert len(get_uncategorised()) == 3

    def test_get_uncategorised_excludes_classified_rows(self):
        insert_transaction({
            "txn_id": "TXN001", "date": "2024-04-01",
            "description": "TESCO", "amount": 42.35,
            "currency": "GBP", "merchant": None, "account_id": None,
        })
        update_category("TXN001", "groceries", 0.97)
        assert len(get_uncategorised()) == 0


# ── Ingest endpoint with classification toggled on ────────────────────────────

class TestIngestWithClassification:
    def test_ingest_classifies_when_enabled(self, client):
        os.environ["CLASSIFY_ON_INGEST"] = "true"
        import app.api.transactions as txn_module
        txn_module.CLASSIFY_ON_INGEST = True

        csv = b"txn_id,date,description,amount\nT1,2024-04-01,TESCO,42.00"

        with patch("app.api.transactions.classify_transaction") as mock_classify:
            mock_classify.return_value = {"category": "groceries", "confidence": 0.97, "reasoning": "Supermarket"}
            with patch("app.api.transactions.update_category") as mock_update:
                response = client.post(
                    "/transactions/ingest",
                    files={"file": ("t.csv", csv, "text/csv")},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["inserted"] == 1
        mock_classify.assert_called_once()
        mock_update.assert_called_once_with("T1", "groceries", 0.97)

        os.environ["CLASSIFY_ON_INGEST"] = "false"
        txn_module.CLASSIFY_ON_INGEST = False

    def test_classification_failure_does_not_fail_ingest(self, client):
        os.environ["CLASSIFY_ON_INGEST"] = "true"
        import app.api.transactions as txn_module
        txn_module.CLASSIFY_ON_INGEST = True

        csv = b"txn_id,date,description,amount\nT1,2024-04-01,TESCO,42.00"

        with patch("app.api.transactions.classify_transaction") as mock_classify:
            mock_classify.side_effect = ClassificationError("API down")
            response = client.post(
                "/transactions/ingest",
                files={"file": ("t.csv", csv, "text/csv")},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["inserted"] == 1          # row still saved
        assert data["classification_errors"] == 1  # error noted but not fatal

        os.environ["CLASSIFY_ON_INGEST"] = "false"
        txn_module.CLASSIFY_ON_INGEST = False