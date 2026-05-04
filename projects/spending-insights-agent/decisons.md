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
