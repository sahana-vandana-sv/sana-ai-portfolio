"""MCP server for the Notes tool set."""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from tools.notes_db import store_note, search_notes

server = Server("lifeagent-notes")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="note_store",
            description="Store a note for the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["user_id", "content"],
            },
        ),
        types.Tool(
            name="note_search",
            description="Semantically search the user's notes",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "query": {"type": "string"},
                },
                "required": ["user_id", "query"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "note_store":
        result = await store_note(**arguments)
    elif name == "note_search":
        result = await search_notes(**arguments)
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
