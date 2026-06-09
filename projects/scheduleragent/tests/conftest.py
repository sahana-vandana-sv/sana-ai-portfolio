"""
Shared pytest configuration.
Loads .env before any test runs so os.environ is populated
(override=True so shell placeholders don't win over the real .env values).
"""
from dotenv import load_dotenv
import pathlib

# Project root is one level above this file (tests/)
ROOT = pathlib.Path(__file__).parent.parent
load_dotenv(ROOT / ".env", override=True)
