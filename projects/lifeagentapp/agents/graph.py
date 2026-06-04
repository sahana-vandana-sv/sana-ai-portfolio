from typing import Any

from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.supervisor import supervisor_node
from agents.calendar_agent import calendar_agent_node
from agents.task_agent import task_agent_node
from agents.notes_agent import notes_agent_node
from agents.memory_agent import memory_agent_node
from agents.responder import responder_node


def route_after_supervisor(state: AgentState) -> list[str]:
    """Fan out to whichever agents the supervisor selected."""
    if state.get("error") == "injection_detected":
        return ["responder"]

    routing = state["routing"]
    destinations = []
    if routing.calendar:
        destinations.append("calendar_agent")
    if routing.task:
        destinations.append("task_agent")
    if routing.note:
        destinations.append("notes_agent")
    if routing.memory:
        destinations.append("memory_agent")

    return destinations or ["responder"]


def build_graph() -> Any:
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("calendar_agent", calendar_agent_node)
    graph.add_node("task_agent", task_agent_node)
    graph.add_node("notes_agent", notes_agent_node)
    graph.add_node("memory_agent", memory_agent_node)
    graph.add_node("responder", responder_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "calendar_agent": "calendar_agent",
            "task_agent": "task_agent",
            "notes_agent": "notes_agent",
            "memory_agent": "memory_agent",
            "responder": "responder",
        },
    )

    for agent in ["calendar_agent", "task_agent", "notes_agent", "memory_agent"]:
        graph.add_edge(agent, "responder")

    graph.add_edge("responder", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


async def run_agent(
    user_id: str,
    chat_id: str,
    message: str,
    short_term_context: list[dict],
) -> dict:
    graph = get_graph()
    initial_state: AgentState = {
        "user_id": user_id,
        "chat_id": chat_id,
        "message": message,
        "routing": None,
        "short_term_context": short_term_context,
        "results": [],
        "reply": "",
        "error": None,
    }
    final_state = await graph.ainvoke(initial_state)
    return {"reply": final_state.get("reply", "Done!"), "results": final_state.get("results", [])}
