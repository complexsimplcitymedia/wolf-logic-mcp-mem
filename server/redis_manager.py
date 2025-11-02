"""
Redis Cache Manager for Wolf-Logic MCP
Handles caching, sessions, and distributed operations
"""

import redis
import json
import logging
from typing import Any, Optional, Callable
from datetime import timedelta
import hashlib
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager with TTL and serialization support"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize Redis connection

        Args:
            redis_url: Redis connection URL
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("✓ Redis connection successful")
            self.connected = True
        except Exception as e:
            logger.warning(f"⚠ Redis connection failed: {e}. Cache will be disabled.")
            self.connected = False
            self.redis_client = None

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments"""
        key_parts = [prefix] + [str(arg) for arg in args]
        # Add sorted kwargs to ensure consistent keys
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend([f"{k}:{v}" for k, v in sorted_kwargs])

        key = ":".join(key_parts)
        # Keep keys under 512 chars by hashing long ones
        if len(key) > 256:
            key = f"{prefix}:{hashlib.md5(key.encode()).hexdigest()}"
        return key

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.connected:
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = 3600,  # Default 1 hour
    ) -> bool:
        """Set value in cache with TTL"""
        if not self.connected:
            return False
        try:
            serialized = json.dumps(value)
            if ttl:
                self.redis_client.setex(key, ttl, serialized)
            else:
                self.redis_client.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.connected:
            return False
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.connected:
            return 0
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing pattern {pattern}: {e}")
            return 0

    def clear_all(self) -> bool:
        """Clear entire cache"""
        if not self.connected:
            return False
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def cache_result(
        self,
        prefix: str,
        ttl: int = 3600,
    ):
        """
        Decorator to cache function results

        Usage:
            @cache.cache_result("search", ttl=3600)
            def search_memories(query: str):
                return expensive_search(query)
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                key = self._generate_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached = self.get(key)
                if cached is not None:
                    logger.debug(f"Cache hit: {key}")
                    return cached

                # Cache miss - execute function
                logger.debug(f"Cache miss: {key}")
                result = func(*args, **kwargs)

                # Store in cache
                self.set(key, result, ttl)
                return result

            return wrapper
        return decorator


class SessionManager:
    """Manage user sessions with Redis"""

    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.session_ttl = 86400 * 7  # 7 days

    def create_session(self, user_id: str, data: dict) -> str:
        """Create new user session"""
        session_key = f"session:{user_id}"
        self.cache.set(session_key, data, self.session_ttl)
        return session_key

    def get_session(self, user_id: str) -> Optional[dict]:
        """Retrieve user session"""
        session_key = f"session:{user_id}"
        return self.cache.get(session_key)

    def update_session(self, user_id: str, data: dict) -> bool:
        """Update user session"""
        return self.create_session(user_id, data) is not None

    def delete_session(self, user_id: str) -> bool:
        """Delete user session"""
        session_key = f"session:{user_id}"
        return self.cache.delete(session_key)

    def get_active_sessions(self) -> list:
        """Get all active sessions"""
        if not self.cache.connected:
            return []
        try:
            keys = self.cache.redis_client.keys("session:*")
            return [key.replace("session:", "") for key in keys]
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []


class RateLimiter:
    """Rate limiting with Redis"""

    def __init__(self, cache: RedisCache):
        self.cache = cache

    def is_allowed(
        self,
        identifier: str,
        max_requests: int = 100,
        window: int = 60,
    ) -> bool:
        """Check if request is allowed (rate limit)"""
        if not self.cache.connected:
            return True  # Allow if Redis is down

        key = f"ratelimit:{identifier}"
        current = self.cache.redis_client.get(key)

        if current is None:
            self.cache.set(key, 1, window)
            return True

        current_count = int(current)
        if current_count >= max_requests:
            return False

        self.cache.redis_client.incr(key)
        return True

    def get_remaining(self, identifier: str, max_requests: int = 100) -> int:
        """Get remaining requests for identifier"""
        if not self.cache.connected:
            return max_requests

        key = f"ratelimit:{identifier}"
        current = self.cache.redis_client.get(key)

        if current is None:
            return max_requests

        return max(0, max_requests - int(current))


class MemoryCache:
    """Specialized cache for memory operations"""

    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.search_ttl = 3600  # 1 hour for searches
        self.memory_ttl = 86400  # 1 day for memory objects
        self.stats_ttl = 300  # 5 minutes for stats

    def cache_search(self, query: str, results: list, user_id: str = "default") -> bool:
        """Cache search results"""
        key = self.cache._generate_key("search", user_id, query)
        return self.cache.set(key, results, self.search_ttl)

    def get_cached_search(self, query: str, user_id: str = "default") -> Optional[list]:
        """Get cached search results"""
        key = self.cache._generate_key("search", user_id, query)
        return self.cache.get(key)

    def invalidate_searches(self, user_id: str = "*") -> int:
        """Invalidate all searches for user"""
        pattern = f"search:{user_id}:*" if user_id != "*" else "search:*"
        return self.cache.clear_pattern(pattern)

    def cache_memory(self, memory_id: str, memory_data: dict) -> bool:
        """Cache memory object"""
        key = f"memory:{memory_id}"
        return self.cache.set(key, memory_data, self.memory_ttl)

    def get_cached_memory(self, memory_id: str) -> Optional[dict]:
        """Get cached memory"""
        key = f"memory:{memory_id}"
        return self.cache.get(key)

    def invalidate_memory(self, memory_id: str) -> bool:
        """Invalidate memory cache"""
        key = f"memory:{memory_id}"
        return self.cache.delete(key)

    def cache_stats(self, stats_key: str, stats_data: dict) -> bool:
        """Cache statistics"""
        key = f"stats:{stats_key}"
        return self.cache.set(key, stats_data, self.stats_ttl)

    def get_cached_stats(self, stats_key: str) -> Optional[dict]:
        """Get cached statistics"""
        key = f"stats:{stats_key}"
        return self.cache.get(key)

    def invalidate_stats(self, stats_key: str = "*") -> int:
        """Invalidate statistics"""
        pattern = f"stats:{stats_key}" if stats_key != "*" else "stats:*"
        return self.cache.clear_pattern(pattern)


# Initialize global instances
redis_cache = None
session_manager = None
rate_limiter = None
memory_cache = None


def init_redis(redis_url: str = "redis://localhost:6379"):
    """Initialize Redis components"""
    global redis_cache, session_manager, rate_limiter, memory_cache

    redis_cache = RedisCache(redis_url)
    session_manager = SessionManager(redis_cache)
    rate_limiter = RateLimiter(redis_cache)
    memory_cache = MemoryCache(redis_cache)

    logger.info("✓ Redis components initialized")
    return redis_cache, session_manager, rate_limiter, memory_cache


def get_redis_cache() -> RedisCache:
    """Get Redis cache instance"""
    if redis_cache is None:
        init_redis()
    return redis_cache

