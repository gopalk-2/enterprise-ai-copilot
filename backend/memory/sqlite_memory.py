"""
Session Memory — Redis-backed with SQLite graceful fallback.

Public API (unchanged):
    init_db()
    add_message(user, role, content)
    get_conversation(user, limit=6)       -> list[dict]
    get_recent_conversation(user, limit=4) -> list[dict]
    clear_conversation(user)

If Redis is available:
    - Messages stored in a Redis List key  `chat:<username>`
    - Each element is a JSON-encoded { role, content, created_at }
    - List is capped at MAX_HISTORY entries via LTRIM after every write

If Redis is unavailable (returns None from redis_client.get_redis()):
    - Falls back transparently to SQLite (original implementation)
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timezone

logger = logging.getLogger("ai_assistant")

# ──────────────────────────────────────────────
# SQLite fallback config (kept identical to original)
# ──────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(current_dir, "../../data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "chat_memory.db")

MAX_HISTORY = 100   # max messages kept per user in Redis


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _redis_key(user: str) -> str:
    return f"chat:{user}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────────────────────
# SQLite helpers (fallback)
# ──────────────────────────────────────────────

def _sqlite_init():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user       TEXT,
            role       TEXT,
            message    TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def _sqlite_add(user: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO chat_history (user, role, message, created_at) VALUES (?,?,?,?)",
        (user, role, content, _now_iso()),
    )
    conn.commit()
    conn.close()


def _sqlite_get(user: str, limit: int) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT role, message FROM chat_history WHERE user=? ORDER BY id DESC LIMIT ?",
        (user, limit),
    )
    rows = cur.fetchall()
    conn.close()
    rows.reverse()
    return [{"role": r, "content": m} for r, m in rows]


def _sqlite_clear(user: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM chat_history WHERE user=?", (user,))
    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def init_db():
    """Initialise SQLite fallback table (no-op when Redis is healthy)."""
    _sqlite_init()


def add_message(user: str, role: str, content: str):
    """Append a message to the user's conversation history."""
    try:
        from memory.redis_client import get_redis
        r = get_redis()
    except Exception:
        r = None

    if r is not None:
        try:
            entry = json.dumps({"role": role, "content": content, "created_at": _now_iso()})
            key = _redis_key(user)
            r.rpush(key, entry)
            r.ltrim(key, -MAX_HISTORY, -1)   # keep only the latest MAX_HISTORY items
            return
        except Exception as exc:
            logger.warning(f"[Redis] add_message failed, falling back to SQLite: {exc}")

    _sqlite_add(user, role, content)


def get_conversation(user: str, limit: int = 6) -> list[dict]:
    """Return the last `limit` messages (oldest → newest)."""
    try:
        from memory.redis_client import get_redis
        r = get_redis()
    except Exception:
        r = None

    if r is not None:
        try:
            key = _redis_key(user)
            raw = r.lrange(key, -limit, -1)
            return [json.loads(e) for e in raw]
        except Exception as exc:
            logger.warning(f"[Redis] get_conversation failed, falling back to SQLite: {exc}")

    return _sqlite_get(user, limit)


def get_recent_conversation(user: str, limit: int = 4) -> list[dict]:
    """Return the most recent `limit` messages (oldest → newest)."""
    return get_conversation(user, limit=limit)


def clear_conversation(user: str):
    """Delete the user's entire conversation history."""
    try:
        from memory.redis_client import get_redis
        r = get_redis()
    except Exception:
        r = None

    if r is not None:
        try:
            r.delete(_redis_key(user))
            return
        except Exception as exc:
            logger.warning(f"[Redis] clear_conversation failed, falling back to SQLite: {exc}")

    _sqlite_clear(user)