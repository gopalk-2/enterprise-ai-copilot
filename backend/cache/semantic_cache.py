"""
Semantic Cache — Redis-backed, sentence-transformer similarity lookup.

Strategy
--------
1. Embed the incoming query using all-MiniLM-L6-v2 (already in requirements).
2. Load all cached embedding vectors from Redis and compute cosine similarity
   in-process with numpy (zero extra services).
3. If best similarity ≥ threshold → cache HIT: return stored answer instantly.
4. On cache MISS: caller runs the full pipeline, then calls `set()` to persist.

Storage schema (Redis Hash per entry)
--------------------------------------
Key pattern : semcache:<hex_id>
Fields      : query, answer, sources_json, embedding_b64, created_at
Index key   : semcache:__index  (Redis Set of all hex_ids)

Configuration (via env vars)
-----------------------------
SEMANTIC_CACHE_TTL_SECONDS   default 86400      (24 h)
SEMANTIC_CACHE_THRESHOLD     default 0.92
"""

import os
import json
import base64
import hashlib
import logging
import threading
from datetime import datetime, timezone
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ai_assistant")

# ── Config ──────────────────────────────────────────────────────────────────
TTL: int = int(os.getenv("SEMANTIC_CACHE_TTL_SECONDS", "86400"))
THRESHOLD: float = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.92"))
INDEX_KEY = "semcache:__index"
MODEL_NAME = "all-MiniLM-L6-v2"


# ── Singleton model ──────────────────────────────────────────────────────────
_model: Optional[SentenceTransformer] = None
_model_lock = threading.Lock()


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                logger.info("[SemanticCache] Loading embedding model…")
                _model = SentenceTransformer(MODEL_NAME)
    return _model


# ── Helpers ──────────────────────────────────────────────────────────────────

def _embed(text: str) -> np.ndarray:
    vec = _get_model().encode(text, normalize_embeddings=True)
    return vec.astype(np.float32)


def _vec_to_b64(vec: np.ndarray) -> str:
    return base64.b64encode(vec.tobytes()).decode()


def _b64_to_vec(b64: str) -> np.ndarray:
    return np.frombuffer(base64.b64decode(b64), dtype=np.float32)


def _entry_key(hex_id: str) -> str:
    return f"semcache:{hex_id}"


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity (both vectors already L2-normalised → just dot product)."""
    return float(np.dot(a, b))


# ── Main class ───────────────────────────────────────────────────────────────

class SemanticCache:
    """Thread-safe semantic cache. Disabled gracefully when Redis is unavailable."""

    def __init__(self):
        self._lock = threading.Lock()

    def _redis(self):
        try:
            from memory.redis_client import get_redis
            return get_redis()   # None if Redis is down
        except Exception:
            return None

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, query: str) -> Optional[dict]:
        """
        Look up `query` in the cache.

        Returns
        -------
        dict  with keys  answer (str), sources (list)   — on HIT
        None                                             — on MISS or error
        """
        r = self._redis()
        if r is None:
            return None

        try:
            query_vec = _embed(query)
            ids = r.smembers(INDEX_KEY)
            if not ids:
                return None

            best_score = -1.0
            best_entry = None

            for hex_id in ids:
                raw = r.hgetall(_entry_key(hex_id))
                if not raw or "embedding_b64" not in raw:
                    continue
                cached_vec = _b64_to_vec(raw["embedding_b64"])
                score = _cosine(query_vec, cached_vec)
                if score > best_score:
                    best_score = score
                    best_entry = raw

            if best_score >= THRESHOLD and best_entry:
                logger.info(f"[SemanticCache] HIT  similarity={best_score:.4f}  query='{query[:60]}'")
                return {
                    "answer": best_entry["answer"],
                    "sources": json.loads(best_entry.get("sources_json", "[]")),
                }

            logger.info(f"[SemanticCache] MISS similarity={best_score:.4f}  query='{query[:60]}'")
            return None

        except Exception as exc:
            logger.warning(f"[SemanticCache] get() error: {exc}")
            return None

    def set(self, query: str, answer: str, sources: list | None = None):
        """
        Store a query→answer pair in the cache.
        Silently skips if Redis is unavailable.
        """
        r = self._redis()
        if r is None:
            return

        try:
            query_vec = _embed(query)
            hex_id = hashlib.sha256(query_vec.tobytes()).hexdigest()[:16]
            key = _entry_key(hex_id)

            entry = {
                "query": query,
                "answer": answer,
                "sources_json": json.dumps(sources or []),
                "embedding_b64": _vec_to_b64(query_vec),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            with self._lock:
                r.hset(key, mapping=entry)
                r.expire(key, TTL)
                r.sadd(INDEX_KEY, hex_id)

            logger.info(f"[SemanticCache] SET  id={hex_id}  ttl={TTL}s  query='{query[:60]}'")

        except Exception as exc:
            logger.warning(f"[SemanticCache] set() error: {exc}")

    def invalidate(self, query: str):
        """Remove a specific cached entry by query similarity (exact match on embedding hash)."""
        r = self._redis()
        if r is None:
            return
        try:
            query_vec = _embed(query)
            hex_id = hashlib.sha256(query_vec.tobytes()).hexdigest()[:16]
            r.delete(_entry_key(hex_id))
            r.srem(INDEX_KEY, hex_id)
        except Exception as exc:
            logger.warning(f"[SemanticCache] invalidate() error: {exc}")

    def clear_all(self):
        """Flush every cache entry — use with care."""
        r = self._redis()
        if r is None:
            return
        try:
            ids = r.smembers(INDEX_KEY)
            for hex_id in ids:
                r.delete(_entry_key(hex_id))
            r.delete(INDEX_KEY)
            logger.info("[SemanticCache] Cache cleared.")
        except Exception as exc:
            logger.warning(f"[SemanticCache] clear_all() error: {exc}")


# ── Module-level singleton ────────────────────────────────────────────────────
semantic_cache = SemanticCache()
