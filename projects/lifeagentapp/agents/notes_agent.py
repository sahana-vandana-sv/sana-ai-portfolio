import structlog
from langsmith import traceable

from agents.state import AgentState
from security.pii_detector import mask_pii
from tools.notes_db import store_note, search_notes

log = structlog.get_logger()


@traceable(name="notes_agent")
async def notes_agent_node(state: AgentState) -> AgentState:
    routing = state["routing"]
    results = list(state.get("results", []))

    try:
        if routing.query:
            hits = await search_notes(
                user_id=state["user_id"],
                query=state["message"],
            )
            results.append({"agent": "notes", "action": "search", "data": hits})
        else:
            safe_content = mask_pii(state["message"])
            note = await store_note(
                user_id=state["user_id"],
                content=safe_content,
                entities=routing.entities,
            )
            results.append({"agent": "notes", "action": "store", "data": note})
            log.info("note_stored", user_id=state["user_id"])
    except Exception as e:
        log.error("notes_agent_error", error=str(e))
        results.append({"agent": "notes", "action": "error", "data": str(e)})

    return {**state, "results": results}
