import json
import logging
from typing import Any, Optional
import redis
from app.core.config import settings

logger = logging.getLogger("app.cache")

class RedisCache:
    def __init__(self):
        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT
        self.db = settings.REDIS_DB
        self.client: Optional[redis.Redis] = None
        self._memory_fallback = {}
        
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                socket_timeout=2.0,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            logger.info(f"Successfully connected to Redis cache at {self.host}:{self.port}")
        except Exception as e:
            logger.warning(f"Redis cache connection failed: {e}. Falling back to in-memory cache.")
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        if self.client:
            try:
                val = self.client.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.error(f"Redis get failed: {e}")
        return self._memory_fallback.get(key)

    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> None:
        if self.client:
            try:
                self.client.setex(key, expire_seconds, json.dumps(value))
                return
            except Exception as e:
                logger.error(f"Redis set failed: {e}")
        self._memory_fallback[key] = value

cache = RedisCache()
