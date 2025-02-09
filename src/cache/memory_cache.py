"""In-memory cache implementation."""

import threading
import time
from typing import Dict, Optional, Tuple

from cache.base import BaseCache
from config.settings import MAX_CACHE_SIZE, CACHE_TTL
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MemoryCache(BaseCache):
    """Thread-safe in-memory cache implementation."""

    def __init__(self, max_size: int = MAX_CACHE_SIZE) -> None:
        """Initialize memory cache.

        Args:
            max_size: Maximum number of items to store in cache
        """
        self.cache: Dict[str, Tuple[str, float]] = {}
        self.max_size = max_size
        self._lock = threading.Lock()
        self.ttl = CACHE_TTL

    def get(self, key: str) -> Optional[str]:
        """Retrieve value from cache if not expired."""
        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    logger.debug("Memory cache hit for key: %s", key)
                    return value
                logger.debug("Memory cache expired for key: %s", key)
                del self.cache[key]
            return None

    def setex(self, key: str, expire_time: int, value: str) -> None:
        """Set value in cache with expiration."""
        with self._lock:
            if len(self.cache) >= self.max_size:
                oldest = min(self.cache.items(), key=lambda x: x[1][1])[0]
                del self.cache[oldest]
                logger.debug("Cache full, removed oldest key: %s", oldest)
            self.cache[key] = (value, time.time())
            logger.debug("Set key in memory cache: %s", key)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self.cache.clear()
            logger.info("Memory cache cleared")
