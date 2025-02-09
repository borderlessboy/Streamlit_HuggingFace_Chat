"""Base cache implementation."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseCache(ABC):
    """Abstract base class for cache implementations."""

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Retrieve value from cache."""

    @abstractmethod
    def setex(self, key: str, expire_time: int, value: str) -> None:
        """Set value in cache with expiration."""

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
