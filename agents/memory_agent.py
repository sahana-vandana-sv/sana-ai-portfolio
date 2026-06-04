import structlog
from langsmith import traceable

from agents.state import AgentState
from tools.memory_store import store_preference, get_preferences

log = structlog.get_logger()


@traceable(name="memory_agent")
async def memory_agent_node(state: AgentState) -> AgentState:
    routing = state["routing"]
    results = list(state.get("results", []))

    try:
        if routing.query:
            prefs = await get_preferences(user_id=state["user_id"])
            results.append({"agent": "memory", "action": "retrieve", "data": prefs})
        else:
            pref = await store_preference(
                user_id=state["user_id"],
                content=state["message"],
                entities=routing.entities,
            )
            results.append({"agent": "memory", "action": "store", "data": pref})
            log.info("preference_stored", user_id=state["user_id"])
    except Exception as e:
        log.error("memory_agent_error", error=str(e))
        results.append({"agent": "memory", "action": "error", "data": str(e)})

    return {**state, "results": results}
