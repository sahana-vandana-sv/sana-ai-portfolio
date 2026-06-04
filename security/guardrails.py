import re

INJECTION_PATTERNS = [
    r"ignore (previous|all|prior) instructions",
    r"disregard (previous|all|prior) instructions",
    r"forget (everything|all instructions)",
    r"you are now",
    r"new system prompt",
    r"delete all (tasks|events|notes|memory|data)",
    r"drop (table|database|schema)",
    r"</?script",
    r"__import__",
    r"eval\(",
    r"exec\(",
]

_compiled = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def check_injection(text: str) -> bool:
    """Return True if the message looks like a prompt injection attempt."""
    for pattern in _compiled:
        if pattern.search(text):
            return True
    return False
