from fastapi import APIRouter,UploadFile,File,HTTPException
from app.db import get_all_transactions, insert_transaction, update_category, get_uncategorised
from app.services.csv_parser import parse_csv_bytes,CSVParseError
from app.services.classifier import classify_transaction , ClassificationError
import os 
"""
Routes:
  POST /transactions/ingest   — upload CSV, classify each transaction via Claude
  GET  /transactions          — list all transactions
  POST /transactions/classify — backfill categories on existing unclassified rows
"""

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

# Classification is skipped in test environments to avoid real API calls
CLASSIFY_ON_INGEST = os.getenv("CLASSIFY_ON_INGEST", "true").lower() == "true"

@router.post("/ingest")
async def ingest_csv(file: UploadFile = File(...)):

#uploads a csv file and returns the summary 
 
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")
    
    content = await file.read()
    try:
        transactions = parse_csv_bytes(content)
    except CSVParseError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    if not transactions:
        raise HTTPException(status_code=422, detail="CSV parsed but contained no valid rows")
    
    inserted=0
    skipped=0
    classified = 0
    classification_errors = 0
    for txn in transactions:
        if insert_transaction(txn):
            inserted+=1

            if CLASSIFY_ON_INGEST:
                try:
                    result = classify_transaction(
                        description=txn["description"],
                        amount=txn["amount"],
                        merchant=txn.get("merchant"),
                    )
                    update_category(txn["txn_id"], result["category"], result["confidence"])
                    classified += 1
                except ClassificationError:
                    # Don't fail the whole ingest if one classification fails
                    # Row is still inserted, just without a category
                    classification_errors += 1
        else:
            skipped+=1  

    return {
        "status": "ok",
        "filename": file.filename,
        "parsed": len(transactions),
        "inserted": inserted,
        "classified": classified,
        "classification_errors": classification_errors,
        "skipped_duplicates": skipped,
    }

@router.post("/classify")
def classify_existing():
    uncategorised = get_uncategorised()
 
    if not uncategorised:
        return {"status": "ok", "message": "All transactions already classified", "classified": 0}
 
    classified = 0
    errors = 0
 
    for txn in uncategorised:
        try:
            result = classify_transaction(
                description=txn["description"],
                amount=txn["amount"],
                merchant=txn.get("merchant"),
            )
            update_category(txn["txn_id"], result["category"], result["confidence"])
            classified += 1
        except ClassificationError:
            errors += 1
 
    return {
        "status": "ok",
        "classified": classified,
        "errors": errors,
    }
 
@router.get("/")
def list_transactions(limit: int = 50, offset: int = 0):
    """
    Return all transactions, newest first.
    Useful for quickly checking what's in the DB without a SQL client.
    """
    all_txns = get_all_transactions()
    return {
        "total": len(all_txns),
        "limit": limit,
        "offset": offset,
        "transactions": all_txns[offset: offset + limit],
    }
    