"""
Redis Cache Configuration

Handles Redis connections and caching operations for the application.
"""

import json
import pickle
import logging
from typing import Any, Optional, Union
from contextlib import asynccontextmanager

import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis connection pool
redis_pool = None


async def init_redis() -> None:
    """Initialize Redis connection pool"""
    global redis_pool
    try:
        redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False,
            max_connections=20,
        )
        logger.info("✅ Redis connection pool initialized")
    except Exception as e:
        logger.error(f"❌ Redis initialization failed: {e}")
        raise


async def get_redis() -> redis.Redis:
    """Get Redis client"""
    if redis_pool is None:
        await init_redis()
    return redis.Redis(connection_pool=redis_pool)


@asynccontextmanager
async def get_redis_client():
    """Context manager for Redis client"""
    client = await get_redis()
    try:
        yield client
    finally:
        await client.close()


class Cache:
    """Redis cache operations wrapper"""
    
    def __init__(self):
        self.default_ttl = settings.REDIS_CACHE_TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            async with get_redis_client() as redis_client:
                value = await redis_client.get(key)
                if value:
                    return pickle.loads(value)
                return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            async with get_redis_client() as redis_client:
                serialized_value = pickle.dumps(value)
                ttl = ttl or self.default_ttl
                await redis_client.setex(key, ttl, serialized_value)
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            async with get_redis_client() as redis_client:
                result = await redis_client.delete(key)
                return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            async with get_redis_client() as redis_client:
                result = await redis_client.exists(key)
                return bool(result)
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            async with get_redis_client() as redis_client:
                keys = await redis_client.keys(pattern)
                if keys:
                    return await redis_client.delete(*keys)
                return 0
        except Exception as e:
            logger.error(f"Cache flush pattern error for {pattern}: {e}")
            return 0


# Global cache instance
cache = Cache()
