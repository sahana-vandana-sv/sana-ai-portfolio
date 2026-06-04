import re

# Simple regex-based PII masking for MVP.
# Can be upgraded to Microsoft Presidio for production.
PII_PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "UK_PHONE": r"(\+44|0)[\s\-]?[0-9]{3,4}[\s\-]?[0-9]{3,4}[\s\-]?[0-9]{3,4}",
    "POSTCODE": r"\b[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}\b",
}

_compiled = {label: re.compile(pattern, re.IGNORECASE) for label, pattern in PII_PATTERNS.items()}


def mask_pii(text: str) -> str:
    for label, pattern in _compiled.items():
        text = pattern.sub(f"[{label}]", text)
    return text


def detect_pii(text: str) -> list[str]:
    """Return list of PII types found in text."""
    return [label for label, pattern in _compiled.items() if pattern.search(text)]
