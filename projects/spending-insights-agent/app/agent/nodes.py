"""
app/agent/nodes.py
 
Three nodes, one responsibility each:
  fetch_node      — pull transactions from DB, compute spend breakdown
  detect_node     — identify anomalies in the fetched window
  summarise_node  — call Claude to write the NL digest
"""
from app.agent.state import AgentState
from datetime import datetime, timedelta
import app.db as db

SUMMARY_SYSTEM = """You are a personal finance assistant writing a daily spending digest.
Be concise, friendly, and specific. Use £ for amounts. No markdown headers.
Structure: one paragraph on overall spend, one on top categories, one on any anomalies.
If no anomalies, end with a brief positive observation or saving tip."""

def fetch_node(state:AgentState) -> AgentState:

    days_back = state.get('days_back', 7)
    cutoff = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    all_txns = db.get_all_transactions()
    window = [t for t in all_txns if t['date'] >= cutoff]

    total = sum(t['amount'] for t in window)
    



