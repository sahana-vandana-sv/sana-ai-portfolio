# classify a transaction description into a spending category.

import os 
import json
import anthropic

CATEGORIES = [
     "groceries",
    "eating_out",
    "transport",
    "subscriptions",
    "shopping",
    "utilities",
    "health",
    "entertainment",
    "other",
    "rent",
]

SYSTEM_PROMPT = f"""You are a transaction classifier for a personal finance app.
Given a transaction description and amount, return a JSON object with exactly these fields:
- category: one of {CATEGORIES}
- confidence: a float between 0.0 and 1.0
- reasoning: one short sentence explaining your choice
 
Return ONLY the JSON object. No markdown, no backticks, no explanation outside the JSON."""

_client = anthropic.Anthropic()

def classify_transaction(description: str, amount: float , merchant : str = None) -> dict:
    user_content = f"Description: {description}\nAmount: £{amount:.2f}"
    if merchant:
        user_content += f"\nMerchant: {merchant}"

    try:
        message =  _client.messages.create(
            model="claude-haiku-4-5-20251001",
            system=SYSTEM_PROMPT,
            max_tokens=150,
            messages=[{"role": "user", "content": user_content}],
        )
    except anthropic.APIError as e:
        raise ClassificationError(f"Claude API error: {e}") 
    
    raw = message.content[0].text.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        raise ClassificationError(f"Claude returned non-JSON: {raw[:100]}")
    
    # Validate the category is one we recognise
    if result.get("category") not in CATEGORIES:
        result["category"] = "other"
        result["confidence"] = 0.0
 
    return {
        "category":   result.get("category", "other"),
        "confidence": float(result.get("confidence", 0.0)),
        "reasoning":  result.get("reasoning", ""),
    }

class ClassificationError(Exception):
    """Raised when classification fails — caller decides whether to retry or fallback."""
    pass
 

