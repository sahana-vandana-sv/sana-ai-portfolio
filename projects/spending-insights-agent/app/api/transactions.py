from fastapi import APIRouter,UploadFile,File,HTTPException
from app.db import get_all_transactions, insert_transaction
from app.services.csv_parser import parse_csv_bytes,CSVParseError

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

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
    for txn in transactions:
        if insert_transaction(txn):
            inserted+=1
        else:
            skipped+=1  

    return {
        "status": "ok",
        "filename": file.filename,
        "parsed": len(transactions),
        "inserted": inserted,
        "skipped_duplicates": skipped,
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
    