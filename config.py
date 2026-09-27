"""
Configuration loader for the EEE Opportunity Tracker.

Reads settings from environment variables (via a .env file, optional)
and from sources.json, which lists the RSS/Atom feeds to check and
the keywords used to describe the user's field of interest.
"""

import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SOURCES_FILE = BASE_DIR / "sources.json"
REPORTS_DIR = BASE_DIR / "reports"
SEEN_FILE = BASE_DIR / "seen_entries.json"


def load_dotenv_if_present():
    """Very small .env loader so users don't need python-dotenv installed."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def get_groq_api_key() -> str:
    load_dotenv_if_present()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key, "
            "or export GROQ_API_KEY in your shell. Get a free key at console.groq.com/keys"
        )
    return api_key


def load_sources() -> dict:
    """Load feed URLs and interest keywords from sources.json."""
    if not SOURCES_FILE.exists():
        raise FileNotFoundError(
            f"{SOURCES_FILE} not found. See sources.example.json for the expected format."
        )
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_dirs():
    REPORTS_DIR.mkdir(exist_ok=True)
