## Day 1

### What I built

- Project scaffold: FastAPI + plain SQLite + raw SQL (no ORM)
- Single `app/db.py` handles all DB operations: init, insert, query
- 50-row seed CSV covering realistic UK spending across 8 merchant categories
- Health endpoint that confirms DB is alive and shows live row count
- Idempotent seed script — INSERT OR IGNORE means safe to re-run
- `pytest.ini` with `pythonpath = .` to fix module resolution
- 10 passing tests across DB ops, CSV validation, and health endpoint

### What I deferred and why

- SQLAlchemy: removed entirely — adds ORM abstraction before the core
  agent work is built. Raw SQL is easier to read and debug at this stage.
- pgvector / Supabase: deferred to Day 9 (deploy day). SQLite is
  sufficient locally and removes all infrastructure setup from Day 1.
- Plaid API: Day 2

### One thing that surprised me technically

- `sqlite3.Row` — by default SQLite rows come back as tuples, so you'd
  write `row[3]` instead of `row["amount"]`. Setting
  `conn.row_factory = sqlite3.Row` makes every row behave like a dict.
  One line, significant readability improvement across all DB functions.

### Decisions I'd defend in an interview

- Raw SQL over ORM: for a solo project with a clear schema and a short
  timeline, an ORM adds indirection with no payoff. The DB layer is
  ~60 lines and trivial to reason about.
- SQLite locally, Postgres on deploy: the swap requires changing only
  `app/db.py` — nothing above it (routes, agent, services) needs to
  change. Clean separation of infrastructure from logic.
- Single `app/db.py` not a `db/` folder: premature structure is its own
  form of complexity. One file handles everything the project needs today.
  Split it when it earns the split.

## Day 2

### What I built

- `app/services/csv_parser.py` — standalone parser that normalises any CSV
  into clean transaction dicts: strips whitespace, coerces types, handles
  multiple date formats, drops null rows with a warning
- `POST /transactions/ingest` — file upload endpoint, returns inserted vs
  skipped count
- `GET /transactions/` — list endpoint for debugging DB state
- 17 passing tests across parser, ingest endpoint, and list endpoint

### What I deferred and why

- Plaid API: timebox decision — CSV path fully validates the ingest
  pipeline. Plaid adds OAuth complexity with no new learning at this stage.
- Authentication on endpoints: Day 9 with the rest of security hardening.

### One thing that surprised me technically

- `TestClient(app)` at module level triggers a real request at import time,
  before any pytest fixture runs. The fix is making `client` a fixture so
  it's created after `fresh_db` patches `db.DB_PATH`. Rule: nothing that
  touches the DB should live at module level in a test file.

### Decisions I'd defend in an interview

- `parse_csv_bytes` and `parse_csv_file` as separate functions: the agent
  on Day 6 will call the parser directly from disk; the API calls it from
  uploaded bytes. Same normalisation logic, two entry points — no HTTP
  round-trip needed from the agent.
- `INSERT OR IGNORE` for deduplication: handled at the DB layer, not
  application logic. Simpler, atomic, and impossible to bypass.
- `CSVParseError` as a named exception: lets the API layer catch it
  specifically and return a clean 422, rather than a generic 500.
