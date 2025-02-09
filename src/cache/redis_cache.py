"""Redis cache implementation."""

from typing import Optional

import redis

from cache.base import BaseCache
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RedisCache(BaseCache):
    """Redis-based cache implementation."""

    def __init__(self, redis_client: redis.Redis) -> None:
        """Initialize Redis cache.

        Args:
            redis_client: Configured Redis client instance
        """
        self.client = redis_client

    def get(self, key: str) -> Optional[str]:
        """Retrieve value from Redis cache."""
        try:
            value = self.client.get(key)
            if value:
                logger.debug("Redis cache hit for key: %s", key)
                return value.decode("utf-8")
            logger.debug("Redis cache miss for key: %s", key)
            return None
        except Exception as e:
            logger.error("Redis get error: %s", e)
            return None

    def setex(self, key: str, expire_time: int, value: str) -> None:
        """Set value in Redis cache with expiration."""
        try:
            self.client.setex(key, expire_time, value)
            logger.debug("Set key in Redis cache: %s", key)
        except Exception as e:
            logger.error("Redis setex error: %s", e)

    def clear(self) -> None:
        """Clear all Redis cache entries."""
        try:
            self.client.flushall()
            logger.info("Redis cache cleared")
        except Exception as e:
            logger.error("Redis clear error: %s", e)
