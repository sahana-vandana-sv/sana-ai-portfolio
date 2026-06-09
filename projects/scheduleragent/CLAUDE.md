# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LifeAgent is a personal life-management assistant delivered as a **Telegram bot**. A user sends a message; a LangGraph pipeline classifies it and fans out to specialised sub-agents (calendar, tasks, notes, memory) that write to external services (Google Calendar, Supabase); a final responder node synthesises a friendly reply that is sent back via Telegram.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server locally
uvicorn api.main:app --reload --port 8000

# Run all tests
pytest

# Run a single test file
pytest tests/test_security.py -v

# Run a single test
pytest tests/test_security.py::test_injection_blocked -v

# Run the routing evaluation suite (requires ANTHROPIC_API_KEY)
python -m eval.eval_suite

# Register the Telegram webhook (run once after deploy)
python -m bot.register_webhook

# Run an MCP server directly (stdio)
python -m mcp_servers.calendar_mcp
```

## Environment Setup

Copy `.env.example` to `.env` and fill in:
- `ANTHROPIC_API_KEY` — required for all LLM calls
- `TELEGRAM_TOKEN` — Telegram bot token
- `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` — Postgres + pgvector backend
- `REDIS_URL` — short-term conversation memory (default `redis://localhost:6379`)
- `GOOGLE_CLIENT_ID/SECRET` — OAuth2 for Google Calendar (produces `token.json` + `credentials.json` on first run)

Run the Supabase schema once: **`infra/schema.sql`** in the Supabase SQL editor (enables pgvector, creates `tasks`, `notes`, `memory` tables and a `match_notes` similarity-search function).

## Architecture

### Request Flow

```
Telegram message
  → POST /webhook/telegram  (api/routes/webhook.py)
  → bot/telegram_handler.py  (fetches Redis context, calls graph, sends reply)
  → agents/graph.py          (LangGraph StateGraph)
      supervisor_node        → RoutingDecision (which agents to invoke)
      ↓ fan-out (parallel)
      calendar_agent_node  / task_agent_node / notes_agent_node / memory_agent_node
      ↓ fan-in
      responder_node         → final reply string
```

### Agent State (`agents/state.py`)

`AgentState` is a `TypedDict` threaded through every node. `RoutingDecision` is a Pydantic model the supervisor populates. Each leaf agent appends `{"agent": str, "action": str, "data": any}` dicts to `state["results"]`; the responder summarises them.

### Supervisor (`agents/supervisor.py`)

Calls `claude-sonnet-4-6` with a structured JSON prompt, parses the response into a `RoutingDecision`. Runs `security.guardrails.check_injection` first — if an injection pattern is detected, the graph short-circuits to the responder immediately via `state["error"] = "injection_detected"`.

### Memory Layers

| Layer | Backing store | Module |
|---|---|---|
| Short-term (conversation) | Redis, 2-hour TTL, last 10 messages | `memory/short_term.py` |
| Long-term preferences | Supabase `memory` table | `tools/memory_store.py` |
| Notes (semantic search) | Supabase `notes` + pgvector 384-dim embeddings (all-MiniLM-L6-v2) | `tools/notes_db.py` |

### MCP Servers (`mcp_servers/`)

Each tool domain is also exposed as a standalone MCP server over stdio (`calendar_mcp.py`, `notes_mcp.py`, `task_mcp.py`). These re-use the same `tools/` implementations and respect `security/permissions.py` before execution.

### Security Layer (`security/`)

- `guardrails.py` — regex-based prompt injection detection (checked in supervisor before any LLM call)
- `pii_detector.py` — `mask_pii` / `detect_pii` for emails and UK phone numbers
- `permissions.py` — allow/deny list consulted by MCP servers

### Frontend (`frontend/`)

React + Vite + Tailwind SPA. Run with `npm run dev` inside `frontend/`. Proxied to the FastAPI backend at `/api`.

## Deployment

Docker Compose (`docker-compose.yml`) runs the FastAPI app + Redis. The ECS task definition lives in `infra/ecs-task-definition.json`. `token.json` and `credentials.json` (Google OAuth) are mounted read-only into the container.

---

## Build Order (Session by Session)

This project is built **one layer at a time**. Each session adds exactly one concern. Don't skip ahead.

| Session | What you build | Done when |
|---------|---------------|-----------|
| **1** ✅ | FastAPI skeleton + `/health` + stub webhook + one real Claude call | `pytest tests/test_api.py` → 3 passed |
| **2** ✅ | Security layer — injection detection + PII masking | `pytest tests/test_security.py` → 27 passed |
| **3** ✅ | Redis short-term memory | `pytest tests/test_memory.py` → 11 passed |
| **4** ✅ | Supabase schema + task tool | `pytest tests/test_tools.py` → 13 passed |
| **5** | Notes tool with pgvector embeddings | semantic search returns ranked results |
| **6** | Memory/preferences tool | store + retrieve preferences |
| **7** | Google Calendar tool + OAuth flow | `create_event` + `list_events` work |
| **8** | LangGraph state + supervisor node | routing decision returned for any message |
| **9** | Leaf agents + responder | `run_agent(...)` returns a real reply |
| **10** | Telegram bot + full webhook | end-to-end Telegram message roundtrip |
| **11** | MCP servers | each server callable over stdio |
| **12** | Eval suite | accuracy score printed |
