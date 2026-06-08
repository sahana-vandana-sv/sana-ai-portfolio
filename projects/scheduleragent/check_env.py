"""
Run this before Session 1 to confirm all key packages are importable.
  python check_env.py
"""
from dotenv import load_dotenv
load_dotenv()

import os

packages = [
    ("fastapi",   "fastapi"),
    ("uvicorn",   "uvicorn"),
    ("anthropic", "anthropic"),
    ("structlog", "structlog"),
    ("httpx",     "httpx"),
    ("pytest",    "pytest"),
]

print("--- package check ---")
for display_name, import_name in packages:
    try:
        __import__(import_name)
        print(f"  OK  {display_name}")
    except ImportError as e:
        print(f"  ERR {display_name}: {e}")

print("\n--- env check ---")
key = os.getenv("ANTHROPIC_API_KEY", "")
if key and key != "your_anthropic_api_key_here":
    print(f"  OK  ANTHROPIC_API_KEY loaded (starts with: {key[:8]}...)")
else:
    print("  ERR ANTHROPIC_API_KEY — open .env and paste your real key")
