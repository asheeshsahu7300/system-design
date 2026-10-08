"""
Thread-safe Storage Layer with Redis Cache-Aside Pattern
Supports:
  - In-memory storage with Read/Write lock protection
  - Redis cache integration with graceful local fallback
  - Click tracking and analytics logs
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from threading import Lock

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


class URLStore:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.redis_client = None
        self._lock = Lock()
        # In-memory primary store
        self._db: Dict[str, Dict[str, Any]] = {}
        # Analytics records: code -> list of click events
        self._analytics: Dict[str, List[Dict[str, Any]]] = {}

    async def init(self):
        """Initializes Redis connection if configured."""
        if self.redis_url and aioredis:
            try:
                self.redis_client = aioredis.from_url(
                    self.redis_url, encoding="utf-8", decode_responses=True
                )
                await self.redis_client.ping()
                print(f"[Storage] Connected to Redis at {self.redis_url}")
            except Exception as e:
                print(f"[Storage] Redis connection failed ({e}). Falling back to in-memory store.")
                self.redis_client = None

    async def save(self, short_code: str, original_url: str, custom_alias: bool = False, expires_at: Optional[str] = None) -> Dict[str, Any]:
        """Saves a shortened URL record."""
        record = {
            "short_code": short_code,
            "original_url": original_url,
            "custom_alias": custom_alias,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at,
            "clicks": 0,
        }

        with self._lock:
            self._db[short_code] = record
            if short_code not in self._analytics:
                self._analytics[short_code] = []

        # Cache in Redis with 1-day TTL
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"url:{short_code}", 86400, json.dumps(record)
                )
            except Exception as e:
                print(f"[Storage] Redis write failed: {e}")

        return record

    async def get(self, short_code: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves original URL record using Cache-Aside strategy:
        1. Check Redis cache
        2. On cache miss, read from DB and write to Redis
        """
        # Step 1: Redis Cache lookup
        if self.redis_client:
            try:
                cached = await self.redis_client.get(f"url:{short_code}")
                if cached:
                    return json.loads(cached)
            except Exception as e:
                print(f"[Storage] Redis get error: {e}")

        # Step 2: Database fallback
        with self._lock:
            record = self._db.get(short_code)

        # Repopulate Redis cache
        if record and self.redis_client:
            try:
                await self.redis_client.setex(
                    f"url:{short_code}", 86400, json.dumps(record)
                )
            except Exception:
                pass

        return record

    async def record_click(self, short_code: str, referrer: Optional[str] = None, user_agent: Optional[str] = None, ip: Optional[str] = None):
        """Asynchronously records click metrics."""
        click_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "referrer": referrer or "Direct",
            "user_agent": user_agent or "Unknown",
            "ip": ip or "127.0.0.1",
        }

        with self._lock:
            if short_code in self._db:
                self._db[short_code]["clicks"] += 1
            if short_code in self._analytics:
                self._analytics[short_code].append(click_event)

        if self.redis_client:
            try:
                await self.redis_client.incr(f"clicks:{short_code}")
            except Exception:
                pass

    async def get_analytics(self, short_code: str) -> Optional[Dict[str, Any]]:
        """Returns analytics payload for a given short code."""
        with self._lock:
            record = self._db.get(short_code)
            clicks = self._analytics.get(short_code, [])

        if not record:
            return None

        return {
            "short_code": short_code,
            "original_url": record["original_url"],
            "total_clicks": record["clicks"],
            "created_at": record["created_at"],
            "recent_clicks": clicks[-50:],  # last 50 events
        }

    async def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns most recently shortened URLs."""
        with self._lock:
            items = list(self._db.values())
        return list(reversed(items[-limit:]))


# Global store singleton
store = URLStore()
