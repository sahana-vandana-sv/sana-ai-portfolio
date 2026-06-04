"""MCP server for the Task tool set.
Run standalone: python -m mcp_servers.task_mcp
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from tools.task_db import create_task, list_tasks, complete_task
from security.permissions import can_execute

server = Server("lifeagent-tasks")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="task_create",
            description="Create a new task for the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "title": {"type": "string"},
                    "due_date": {"type": "string", "nullable": True},
                },
                "required": ["user_id", "title"],
            },
        ),
        types.Tool(
            name="task_list",
            description="List incomplete tasks for the user",
            inputSchema={
                "type": "object",
                "properties": {"user_id": {"type": "string"}},
                "required": ["user_id"],
            },
        ),
        types.Tool(
            name="task_complete",
            description="Mark a task as complete",
            inputSchema={
                "type": "object",
                "properties": {"task_id": {"type": "string"}},
                "required": ["task_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if not can_execute({"task_create": "create_task", "task_list": "list_tasks", "task_complete": "complete_task"}.get(name, name)):
        return [types.TextContent(type="text", text="Permission denied")]

    if name == "task_create":
        result = await create_task(**arguments)
    elif name == "task_list":
        result = await list_tasks(**arguments)
    elif name == "task_complete":
        result = await complete_task(**arguments)
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
