from fastapi import APIRouter
from app.db import get_transaction_count

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    """
    Confirms the app is running and the DB is reachable.
    Returns transaction count so you can verify the seed worked.
    """
    try:
        count = get_transaction_count()
        db_status = "ok"
    except Exception as e:
        count = None
        db_status = f"error: {e}"

    return {
        "status": "ok",
        "db": db_status,
        "transactions_in_db": count,
    }