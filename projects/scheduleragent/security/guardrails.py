import re
from typing import List

_INJECTION_PATTERNS: List[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r'ignore\s+(all\s+)?previous\s+instructions?',
        r'forget\s+(your\s+)?(previous\s+)?instructions?',
        r'you\s+are\s+now\b',
        r'\bact\s+as\b',
        r'pretend\s+(you\s+are|to\s+be)',
        r'(reveal|print|show|display)\s+.*?(system\s+prompt|your\s+(instructions?|prompt))',
        r'\bsystem\s+prompt\b',
        r'\bDAN\b',
        r'\[INST\]',
        r'disregard\s+(all\s+)?instructions?',
        r'(new\s+instructions?|override\s+instructions?)',
    ]
]


def check_injection(text: str) -> bool:
    """Return True if text is safe, False if a prompt injection pattern is detected."""
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            return False
    return True
