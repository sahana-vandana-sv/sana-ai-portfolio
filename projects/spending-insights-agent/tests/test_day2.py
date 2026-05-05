"""
Day 2 tests — CSV parser + ingest endpoint.
Run: pytest tests/test_day2.py -v
"""
import os
import pytest

# Must be set before any app module is imported
os.environ["DB_PATH"] = "data/test.db"

from fastapi.testclient import TestClient
from app.main import app
import app.db as db
from app.services.csv_parser import parse_csv_bytes, parse_csv_file, CSVParseError

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    """Point db module at a temp file and re-initialise before each test."""
    test_db = str(tmp_path / "test.db")
    db.DB_PATH = test_db
    db.init_db()
    yield
    db.DB_PATH = "data/test.db"


# ── CSV Parser ────────────────────────────────────────────────────────────────

class TestCSVParser:
    def test_parse_seed_csv(self):
        txns = parse_csv_file("data/seed_transactions.csv")
        assert len(txns) == 50

    def test_returns_list_of_dicts(self):
        txns = parse_csv_file("data/seed_transactions.csv")
        assert isinstance(txns[0], dict)

    def test_required_fields_present(self):
        txns = parse_csv_file("data/seed_transactions.csv")
        for txn in txns:
            assert "txn_id" in txn
            assert "date" in txn
            assert "description" in txn
            assert "amount" in txn

    def test_amount_is_float(self):
        txns = parse_csv_file("data/seed_transactions.csv")
        assert all(isinstance(t["amount"], float) for t in txns)

    def test_date_normalised_to_yyyy_mm_dd(self):
        txns = parse_csv_file("data/seed_transactions.csv")
        for txn in txns:
            parts = txn["date"].split("-")
            assert len(parts) == 3 and len(parts[0]) == 4

    def test_missing_required_column_raises(self):
        bad_csv = b"date,description,amount\n2024-01-01,Coffee,5.00"
        with pytest.raises(CSVParseError) as exc:
            parse_csv_bytes(bad_csv)
        assert "txn_id" in str(exc.value)

    def test_alternate_date_format(self):
        csv = b"txn_id,date,description,amount\nT1,01/04/2024,Tesco,42.00"
        txns = parse_csv_bytes(csv)
        assert txns[0]["date"] == "2024-04-01"

    def test_extra_columns_are_ignored(self):
        csv = b"txn_id,date,description,amount,extra_col\nT1,2024-04-01,Tesco,42.00,ignore_me"
        txns = parse_csv_bytes(csv)
        assert "extra_col" not in txns[0]

    def test_null_rows_are_dropped(self):
        csv = b"txn_id,date,description,amount\nT1,2024-04-01,Tesco,42.00\n,,,"
        txns = parse_csv_bytes(csv)
        assert len(txns) == 1


# ── Ingest Endpoint ───────────────────────────────────────────────────────────

class TestIngestEndpoint:
    def _upload(self, content: bytes, filename="test.csv"):
        return client.post(
            "/transactions/ingest",
            files={"file": (filename, content, "text/csv")},
        )

    def test_ingest_seed_csv(self):
        with open("data/seed_transactions.csv", "rb") as f:
            content = f.read()
        response = self._upload(content, "seed_transactions.csv")
        assert response.status_code == 200
        data = response.json()
        assert data["inserted"] == 50
        assert data["skipped_duplicates"] == 0

    def test_duplicate_upload_skips_all(self):
        with open("data/seed_transactions.csv", "rb") as f:
            content = f.read()
        self._upload(content)
        response = self._upload(content)
        data = response.json()
        assert data["inserted"] == 0
        assert data["skipped_duplicates"] == 50

    def test_partial_duplicate(self):
        first  = b"txn_id,date,description,amount\nT1,2024-04-01,Tesco,42.00"
        second = b"txn_id,date,description,amount\nT1,2024-04-01,Tesco,42.00\nT2,2024-04-02,Pret,8.50"
        self._upload(first)
        response = self._upload(second)
        data = response.json()
        assert data["inserted"] == 1
        assert data["skipped_duplicates"] == 1

    def test_rejects_non_csv(self):
        response = self._upload(b"not a csv", filename="data.txt")
        assert response.status_code == 400

    def test_rejects_csv_missing_required_columns(self):
        bad = b"date,description,amount\n2024-01-01,Coffee,5.00"
        response = self._upload(bad)
        assert response.status_code == 422

    def test_response_shape(self):
        csv = b"txn_id,date,description,amount\nT1,2024-04-01,Tesco,42.00"
        response = self._upload(csv)
        data = response.json()
        assert "inserted" in data
        assert "skipped_duplicates" in data
        assert "parsed" in data


# ── List Endpoint ─────────────────────────────────────────────────────────────

class TestListEndpoint:
    def test_empty_db_returns_empty_list(self):
        response = client.get("/transactions/")
        assert response.status_code == 200
        assert response.json()["transactions"] == []

    def test_returns_inserted_transactions(self):
        csv = b"txn_id,date,description,amount\nT1,2024-04-01,Tesco,42.00"
        client.post("/transactions/ingest", files={"file": ("t.csv", csv, "text/csv")})
        response = client.get("/transactions/")
        assert response.json()["total"] == 1