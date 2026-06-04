import structlog
from langsmith import traceable

from agents.state import AgentState
from tools.task_db import create_task, list_tasks

log = structlog.get_logger()


@traceable(name="task_agent")
async def task_agent_node(state: AgentState) -> AgentState:
    routing = state["routing"]
    entities = routing.entities
    results = list(state.get("results", []))

    try:
        if routing.query:
            tasks = await list_tasks(user_id=state["user_id"])
            results.append({"agent": "task", "action": "list", "data": tasks})
        else:
            title = entities.get("title") or state["message"][:120]
            due = entities.get("datetime")
            task = await create_task(
                user_id=state["user_id"],
                title=title,
                due_date=due,
            )
            results.append({"agent": "task", "action": "create", "data": task})
            log.info("task_created", title=title)
    except Exception as e:
        log.error("task_agent_error", error=str(e))
        results.append({"agent": "task", "action": "error", "data": str(e)})

    return {**state, "results": results}
