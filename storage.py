"""Simple token storage utilities.

Uses a small JSON file in the project directory to persist a single access token.
This is intentionally simple for reviewer/demo flows. In production, use a secure
secrets store or database.
"""
import json
from pathlib import Path
from typing import Optional

STORE_PATH = Path(__file__).parent / "data"
STORE_PATH.mkdir(exist_ok=True)
TOKEN_FILE = STORE_PATH / "token.json"


def save_token(token: str) -> None:
    TOKEN_FILE.write_text(json.dumps({"access_token": token}))


def load_token() -> Optional[str]:
    if not TOKEN_FILE.exists():
        return None
    try:
        data = json.loads(TOKEN_FILE.read_text())
        return data.get("access_token")
    except Exception:
        return None


def clear_token() -> None:
    try:
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
    except Exception:
        pass
