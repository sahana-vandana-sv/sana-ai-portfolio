"""MCP server for the Calendar tool set."""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from tools.google_calendar import create_event, list_events, delete_event
from security.permissions import can_execute

server = Server("lifeagent-calendar")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="event_create",
            description="Create a calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "start_datetime": {"type": "string", "nullable": True},
                },
                "required": ["title"],
            },
        ),
        types.Tool(
            name="event_list",
            description="List upcoming calendar events",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="event_delete",
            description="Delete a calendar event by ID",
            inputSchema={
                "type": "object",
                "properties": {"event_id": {"type": "string"}},
                "required": ["event_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    tool_map = {"event_create": "create_event", "event_list": "list_events", "event_delete": "delete_event"}
    if not can_execute(tool_map.get(name, name)):
        return [types.TextContent(type="text", text="Permission denied")]

    if name == "event_create":
        result = await create_event(**arguments)
    elif name == "event_list":
        result = await list_events()
    elif name == "event_delete":
        result = await delete_event(**arguments)
    else:
        result = {"error": f"Unknown tool: {name}"}

    import json
    return [types.TextContent(type="text", text=json.dumps(result))]


async def main():
    async with stdio_server() as streams:
        await server.run(*streams, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
