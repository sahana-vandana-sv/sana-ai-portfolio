import os

import structlog
from anthropic import AsyncAnthropic
from langsmith import traceable

from agents.state import AgentState

log = structlog.get_logger()

client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a friendly personal life assistant.
Given the results of actions taken on behalf of the user, compose a short,
friendly confirmation message. Be concise (1-3 sentences).
Mention what was done and any relevant details like dates or titles.
If there were errors, apologise briefly and say you'll try again."""


@traceable(name="responder")
async def responder_node(state: AgentState) -> AgentState:
    if state.get("error") == "injection_detected":
        return state

    results_summary = "\n".join(
        f"- {r['agent']} {r['action']}: {r['data']}" for r in state.get("results", [])
    )

    if not results_summary:
        results_summary = "No actions were taken."

    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"User said: {state['message']}\n\nActions taken:\n{results_summary}",
            }
        ],
    )

    reply = response.content[0].text.strip()
    return {**state, "reply": reply}
