"""Tool permission tiers."""

READ = "read"
WRITE = "write"
DELETE = "delete"

TOOL_PERMISSIONS: dict[str, str] = {
    "list_tasks": READ,
    "list_events": READ,
    "search_notes": READ,
    "get_preferences": READ,
    "create_task": WRITE,
    "create_event": WRITE,
    "store_note": WRITE,
    "store_preference": WRITE,
    "complete_task": WRITE,
    "delete_event": DELETE,
}

# Delete actions are disabled by default.
DELETE_ENABLED = False


def can_execute(tool_name: str) -> bool:
    tier = TOOL_PERMISSIONS.get(tool_name, WRITE)
    if tier == DELETE and not DELETE_ENABLED:
        return False
    return True
