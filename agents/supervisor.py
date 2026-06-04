import json
import os

import structlog
from anthropic import AsyncAnthropic
from langsmith import traceable

from agents.state import AgentState, RoutingDecision
from security.guardrails import check_injection

log = structlog.get_logger()

client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are the supervisor for a Personal Life OS Agent.
Analyze the user's message and decide which agents should handle it.

Respond ONLY with valid JSON matching this schema:
{
  "calendar": bool,   // create/update/query events, meetings, reminders
  "task": bool,       // create/update/complete tasks or to-dos
  "note": bool,       // store knowledge, preferences-as-notes
  "memory": bool,     // store long-term preferences or habits
  "query": bool,      // user wants a summary or to retrieve information
  "confidence": float, // 0.0-1.0
  "entities": {
    "datetime": "ISO string or null",
    "title": "string or null",
    "amount": "float or null",
    "currency": "string or null",
    "person": "string or null",
    "raw_date": "string or null"
  }
}

Examples:
- "Remind me to call GP next Thursday at 10am" → calendar:true, task:true
- "I spent £18 on lunch with Sarah" → note:true, entities with amount/person
- "Remember that I prefer morning gym sessions" → memory:true
- "Summarize everything I need to do this week" → query:true
"""


@traceable(name="supervisor")
async def supervisor_node(state: AgentState) -> AgentState:
    message = state["message"]

    injection = check_injection(message)
    if injection:
        log.warning("injection_blocked", message=message[:100])
        return {
            **state,
            "routing": RoutingDecision(),
            "reply": "I can't process that request.",
            "error": "injection_detected",
        }

    context_str = ""
    if state.get("short_term_context"):
        recent = state["short_term_context"][-4:]
        context_str = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )

    user_content = f"{context_str}\nUSER: {message}" if context_str else message

    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw = response.content[0].text.strip()

    try:
        data = json.loads(raw)
        routing = RoutingDecision(**data)
    except Exception:
        log.warning("routing_parse_failed", raw=raw[:200])
        routing = RoutingDecision(task=True, confidence=0.5)

    log.info("routing_decision", routing=routing.model_dump())
    return {**state, "routing": routing, "results": [], "error": None}
