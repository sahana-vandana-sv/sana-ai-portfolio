import re
from dataclasses import dataclass
from typing import List

_EMAIL_RE = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
)

# Covers: 07xxx xxxxxx, +44 7xxx xxxxxx, 01xx xxxxxx, 020 xxxx xxxx, etc.
_UK_PHONE_RE = re.compile(
    r'(\+44[\s\-]?(\(0\)[\s\-]?)?|0)'
    r'(7\d{3}[\s\-]?\d{6}'           # mobile: 07xxx xxxxxx
    r'|[1-9]\d{3}[\s\-]?\d{6}'       # landline 5-digit area: 01234 567890
    r'|[1-9]\d[\s\-]?\d{4}[\s\-]?\d{4}'    # landline 3-digit area: 020 xxxx xxxx
    r'|[1-9]\d{2}[\s\-]?\d{3}[\s\-]?\d{4})'  # landline 4-digit area: 0121 xxx xxxx
)


@dataclass
class PiiMatch:
    pii_type: str   # "EMAIL" or "PHONE"
    value: str


def detect_pii(text: str) -> List[PiiMatch]:
    """Detect emails and UK phone numbers in text, returning a list of PiiMatch objects."""
    results: List[PiiMatch] = []
    for m in _EMAIL_RE.finditer(text):
        results.append(PiiMatch(pii_type="EMAIL", value=m.group()))
    for m in _UK_PHONE_RE.finditer(text):
        results.append(PiiMatch(pii_type="PHONE", value=m.group()))
    return results


def mask_pii(text: str) -> str:
    """Replace emails with [EMAIL] and UK phone numbers with [PHONE]."""
    text = _EMAIL_RE.sub("[EMAIL]", text)
    text = _UK_PHONE_RE.sub("[PHONE]", text)
    return text
