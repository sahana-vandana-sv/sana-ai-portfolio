from typing import TypedDict, Any
from pydantic import BaseModel


class RoutingDecision(BaseModel):
    calendar: bool = False
    task: bool = False
    note: bool = False
    memory: bool = False
    query: bool = False  # read/summary request
    confidence: float = 1.0
    entities: dict[str, Any] = {}


class AgentState(TypedDict):
    user_id: str
    chat_id: str
    message: str
    routing: RoutingDecision | None
    short_term_context: list[dict]
    results: list[dict]
    reply: str
    error: str | None
