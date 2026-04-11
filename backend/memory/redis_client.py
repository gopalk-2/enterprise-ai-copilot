"""
Redis Client — Singleton Connection Pool
Reads REDIS_URL from environment (default: redis://localhost:6379).
Used by session memory and semantic cache.
"""

import os
import logging
import redis
from redis import ConnectionPool, Redis
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ai_assistant")

REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

_pool: ConnectionPool | None = None


def _get_pool() -> ConnectionPool:
    """Lazily initialise a single connection pool for the process lifetime."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(
            REDIS_URL,
            decode_responses=True,   # all keys/values are Python str
            max_connections=20,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return _pool


def get_redis() -> Redis | None:
    """
    Return a Redis client sharing the global connection pool.
    Returns None (and logs a warning) if Redis is unavailable so callers
    can fall back gracefully.
    """
    try:
        client = Redis(connection_pool=_get_pool())
        client.ping()          # fast health-check
        return client
    except Exception as exc:
        logger.warning(f"[Redis] Unavailable – falling back to SQLite. Reason: {exc}")
        return None
