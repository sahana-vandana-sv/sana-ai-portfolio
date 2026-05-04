#Load seed_transactions.csv into the SQLite database.

import pandas as pd
from app.db import init_db,insert_transaction

def seed():
    init_db()

    df=pd.read_csv("data/seed_transactions.csv")
    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        was_inserted = insert_transaction({
            "txn_id":      row["txn_id"],
            "date":        row["date"],
            "description": row["description"],
            "amount":      float(row["amount"]),
            "currency":    row["currency"],
            "merchant":    row["merchant"],
            "account_id":  row["account_id"],
        })
        if was_inserted:
            inserted += 1
        else:
            skipped += 1

    print(f"Inserted {inserted} transactions, skipped {skipped} duplicates.")


if __name__ == "__main__":    seed()


