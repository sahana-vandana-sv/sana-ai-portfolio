from fastapi import APIRouter,UploadFile,File,HTTPException
from app.db import (get_all_transactions, insert_transaction, update_category, get_uncategorised, update_anomaly, get_transactions_by_category, get_anomalies,)
from app.services.csv_parser import parse_csv_bytes,CSVParseError
from app.services.classifier import classify_transaction , ClassificationError
from app.services.anomaly import detect_anomalies_bulk, detect_anomaly
import os 
"""
Routes:
  POST /transactions/ingest   — upload CSV, classify each transaction via Claude
  POST /transactions/classify    — backfill categories on unclassified rows
  POST /transactions/detect      — run anomaly detection across all categorised rows
  GET  /transactions/anomalies   — list all flagged anomalies
  GET  /transactions             — list all transactions
"""

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

# Classification is skipped in test environments to avoid real API calls
CLASSIFY_ON_INGEST = os.getenv("CLASSIFY_ON_INGEST", "true").lower() == "true"

@router.post("/ingest")
async def ingest_csv(file: UploadFile = File(...)):

#uploads a csv  — insert, classify, and anomaly-check each new transaction
 
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
    anomalies_found = 0
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

                    # Run anomaly check against existing transactions in same category
                    peers = get_transactions_by_category(result["category"])
                    anomaly_result = detect_anomaly(txn, peers)
                    update_anomaly(txn["txn_id"], anomaly_result["is_anomaly"])
                    if anomaly_result["is_anomaly"]:
                        anomalies_found += 1
                        
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
        "anomalies_found": anomalies_found,
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

@router.post("/detect")
def run_anomaly_detection():
    # Run anomaly detection across all categorised transactions.
    #Updates is_anomaly flag on each row.

    all_txns = get_all_transactions()
    categorised = [t for t in all_txns if t.get("category")]

    if not categorised:
        return {"status": "ok", "message": "No categorised transactions to analyse", "anomalies": 0}
    
    results = detect_anomalies_bulk(categorised)
    anomalies = 0

    for result in results:
        is_anomaly = result["anomaly_detail"]["is_anomaly"]
        update_anomaly(result["txn_id"], is_anomaly)
        if is_anomaly:
            anomalies += 1

    return {
        "status": "ok",
        "analysed": len(results),
        "anomalies_found": anomalies,
    }

@router.get("/anomalies")
def list_anomalies():
 #return all transactions flagged as anomalies for review
    anomalies = get_anomalies()
    return {
        "total": len(anomalies),
        "anomalies": anomalies,
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
    