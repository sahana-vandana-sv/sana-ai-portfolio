import sqlite3
import os 

DB_PATH=os.getenv("DB_PATH","data/spending.db")

def get_connection():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            txn_id      TEXT UNIQUE NOT NULL,
            date        TEXT NOT NULL,
            description TEXT NOT NULL,
            amount      REAL NOT NULL,
            currency    TEXT DEFAULT 'GBP',
            merchant    TEXT,
            account_id  TEXT,
            category    TEXT,       -- filled by Claude on Day 3
            is_anomaly  INTEGER DEFAULT 0,  -- 0=false, 1=true, filled Day 5
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

#Insert a single transaction. Returns True if inserted, False if duplicate.
def insert_transaction(txn:dict)->bool:
    conn = get_connection()
    cursor = conn.execute("""
        INSERT OR IGNORE INTO transactions
            (txn_id, date, description, amount, currency, merchant, account_id)
        VALUES
            (:txn_id, :date, :description, :amount, :currency, :merchant, :account_id)
    """, txn)
    conn.commit()
    inserted = cursor.rowcount==1
    conn.close()
    return inserted

#"""Return all transactions as a list of dicts."""
def get_all_transactions():
    conn=get_connection()
    rows=conn.execute("SELECT * FROM transactions ORDER BY date DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_transaction_count():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    conn.close()
    return count


# category 

def update_category(txn_id: str, category: str, confidence: float)-> None:
    conn = get_connection()
    conn.execute("""
        UPDATE transactions
        SET category = ?
        WHERE txn_id = ?
    """, (category, txn_id))
    conn.commit()
    conn.close()

def get_uncategorised() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE category IS NULL ORDER BY date DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows] 


