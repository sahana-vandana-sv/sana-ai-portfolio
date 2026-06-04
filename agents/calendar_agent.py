import structlog
from langsmith import traceable

from agents.state import AgentState
from tools.google_calendar import create_event, list_events

log = structlog.get_logger()


@traceable(name="calendar_agent")
async def calendar_agent_node(state: AgentState) -> AgentState:
    routing = state["routing"]
    entities = routing.entities
    results = list(state.get("results", []))

    try:
        if routing.query:
            events = await list_events()
            results.append({"agent": "calendar", "action": "list", "data": events})
        else:
            title = entities.get("title") or state["message"][:80]
            dt = entities.get("datetime")
            event = await create_event(title=title, start_datetime=dt)
            results.append({"agent": "calendar", "action": "create", "data": event})
            log.info("calendar_event_created", title=title)
    except Exception as e:
        log.error("calendar_agent_error", error=str(e))
        results.append({"agent": "calendar", "action": "error", "data": str(e)})

    return {**state, "results": results}
