"""
Confirmation token storage.

Tokens are stored as Redis hashes with a TTL. Each token represents a single
change request and progresses through statuses:

    pending_user      → just created, waiting for the customer to click confirm
    pending_support   → customer confirmed, waiting for support to approve
    approved          → support approved, flow complete (then token is deleted)

If Upstash credentials aren't set, falls back to an in-memory dict. This is
useful for local development but **does not work in production** — Vercel
serverless instances don't share memory, and the dict is wiped between
invocations.
"""

import os
import secrets
import time
from typing import Optional

TOKEN_TTL_SECONDS = 15 * 60  # 15 minutes

# Status values
STATUS_PENDING_USER = "pending_user"
STATUS_PENDING_SUPPORT = "pending_support"
STATUS_APPROVED = "approved"


class _MemoryStore:
    """Fallback in-memory store. Tokens get wiped on restart and don't persist
    across Vercel serverless invocations — use Upstash for production."""

    def __init__(self):
        self._data: dict[str, dict[str, str]] = {}
        self._expiry: dict[str, float] = {}

    def _expired(self, key: str) -> bool:
        exp = self._expiry.get(key)
        if exp is None:
            return False
        if time.time() > exp:
            self._data.pop(key, None)
            self._expiry.pop(key, None)
            return True
        return False

    def set(self, key: str, data: dict, ttl: int):
        self._data[key] = {k: str(v) for k, v in data.items()}
        self._expiry[key] = time.time() + ttl

    def get(self, key: str) -> Optional[dict]:
        if self._expired(key):
            return None
        return self._data.get(key)

    def update(self, key: str, patch: dict):
        if self._expired(key) or key not in self._data:
            return
        self._data[key].update({k: str(v) for k, v in patch.items()})

    def clear_expiry(self, key: str):
        """Remove the expiry from a key, making it permanent (until deleted)."""
        self._expiry.pop(key, None)

    def delete(self, key: str):
        self._data.pop(key, None)
        self._expiry.pop(key, None)


_memory = _MemoryStore()
_redis = None


def _get_redis():
    """Lazy import & init so the app starts even if upstash isn't installed."""
    global _redis
    if _redis is not None:
        return _redis
    if not (os.environ.get("UPSTASH_REDIS_REST_URL") and os.environ.get("UPSTASH_REDIS_REST_TOKEN")):
        return None
    try:
        from upstash_redis import Redis
        _redis = Redis.from_env()
        return _redis
    except ImportError:
        return None


def using_redis() -> bool:
    """For the /api/debug endpoint to report which backend is active."""
    return _get_redis() is not None


def create_token(payload: dict) -> str:
    """Generate a fresh token and store the payload. Returns the token string."""
    token = secrets.token_urlsafe(32)
    data = {
        **payload,
        "status": STATUS_PENDING_USER,
        "created_at": str(int(time.time())),
    }

    redis = _get_redis()
    if redis:
        redis.hset(f"token:{token}", values=data)
        redis.expire(f"token:{token}", TOKEN_TTL_SECONDS)
    else:
        _memory.set(f"token:{token}", data, TOKEN_TTL_SECONDS)

    return token


def get_token(token: str) -> Optional[dict]:
    """Fetch token data. Returns None if missing or expired."""
    key = f"token:{token}"
    redis = _get_redis()
    if redis:
        data = redis.hgetall(key)
        return dict(data) if data else None
    return _memory.get(key)


def update_status(token: str, new_status: str, *, clear_expiry: bool = False):
    """Advance the token's status.

    By default the existing TTL is preserved. Pass clear_expiry=True to make
    the token live indefinitely (used when handing off to customer support,
    who needs unlimited time to approve).
    """
    key = f"token:{token}"
    patch = {"status": new_status, "updated_at": str(int(time.time()))}

    redis = _get_redis()
    if redis:
        redis.hset(key, values=patch)
        if clear_expiry:
            # Upstash's PERSIST removes any existing TTL, making the key permanent
            # until explicitly deleted.
            redis.persist(key)
    else:
        _memory.update(key, patch)
        if clear_expiry:
            _memory.clear_expiry(key)


def delete_token(token: str):
    """Remove a token (called after the flow completes)."""
    key = f"token:{token}"
    redis = _get_redis()
    if redis:
        redis.delete(key)
    else:
        _memory.delete(key)