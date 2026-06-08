from typing import Set

# Explicit allow list — only these operations may be executed by MCP servers
ALLOWED_OPERATIONS: Set[str] = {
    "calendar.list_events",
    "calendar.create_event",
    "tasks.list_tasks",
    "tasks.create_task",
    "notes.search_notes",
    "notes.create_note",
    "memory.get_preference",
    "memory.set_preference",
}

# Explicit deny list — takes precedence over the allow list
DENIED_OPERATIONS: Set[str] = {
    "calendar.delete_all",
    "tasks.delete_all",
    "admin.reset",
}


def is_allowed(operation: str) -> bool:
    """
    Return True if the operation is permitted.
    Deny list takes precedence; anything not on the allow list is denied by default.
    """
    if operation in DENIED_OPERATIONS:
        return False
    return operation in ALLOWED_OPERATIONS


def add_to_allowlist(operation: str) -> None:
    """Add an operation to the allow list."""
    ALLOWED_OPERATIONS.add(operation)


def add_to_denylist(operation: str) -> None:
    """Add an operation to the deny list."""
    DENIED_OPERATIONS.add(operation)
