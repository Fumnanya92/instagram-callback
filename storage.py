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
    try:
        TOKEN_FILE.write_text(json.dumps({"access_token": token}))
        print(f"Saved access token to {TOKEN_FILE}")
    except Exception as e:
        # Don't crash the app on save errors; log for debugging
        print(f"Failed to save token to {TOKEN_FILE}: {e}")


def load_token() -> Optional[str]:
    if not TOKEN_FILE.exists():
        return None
    try:
        data = json.loads(TOKEN_FILE.read_text())
        return data.get("access_token")
    except Exception:
        print(f"Failed to read token file {TOKEN_FILE}")
        return None


def clear_token() -> None:
    try:
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
    except Exception:
        pass
