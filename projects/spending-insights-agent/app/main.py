from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.transactions import router as transactions_router

app = FastAPI(
    title="Spending Insights Agent",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(transactions_router)

@app.get("/")
def root():
    return {"message": "Spending Insights Agent — see /docs"}