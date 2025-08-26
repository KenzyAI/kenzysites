"""
Advanced Cache Service for KenzySites
"""

import redis
import json
import hashlib
import pickle
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import asyncio
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live based

class CacheLevel(Enum):
    """Cache levels"""
    MEMORY = "memory"  # In-memory cache
    REDIS = "redis"  # Redis cache
    CDN = "cdn"  # CDN cache

class CacheService:
    """Advanced multi-level cache service"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        memory_size_mb: int = 100,
        default_ttl: int = 3600
    ):
        self.redis_client = redis.from_url(redis_url)
        self.memory_cache: Dict[str, Any] = {}
        self.memory_metadata: Dict[str, Dict] = {}
        self.memory_size_limit = memory_size_mb * 1024 * 1024  # Convert to bytes
        self.current_memory_size = 0
        self.default_ttl = default_ttl
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "memory_hits": 0,
            "redis_hits": 0,
            "evictions": 0
        }
    
    def cache_key(self, namespace: str, key: str) -> str:
        """Generate cache key with namespace"""
        return f"kenzysites:{namespace}:{key}"
    
    def hash_key(self, data: Any) -> str:
        """Generate hash key from data"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def get(
        self,
        namespace: str,
        key: str,
        levels: List[CacheLevel] = None
    ) -> Optional[Any]:
        """Get value from cache"""
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS]
        
        cache_key = self.cache_key(namespace, key)
        
        # Try memory cache first
        if CacheLevel.MEMORY in levels:
            value = self._get_from_memory(cache_key)
            if value is not None:
                self.cache_stats["hits"] += 1
                self.cache_stats["memory_hits"] += 1
                return value
        
        # Try Redis cache
        if CacheLevel.REDIS in levels:
            value = await self._get_from_redis(cache_key)
            if value is not None:
                self.cache_stats["hits"] += 1
                self.cache_stats["redis_hits"] += 1
                
                # Promote to memory cache
                if CacheLevel.MEMORY in levels:
                    self._set_in_memory(cache_key, value)
                
                return value
        
        self.cache_stats["misses"] += 1
        return None
    
    async def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: int = None,
        levels: List[CacheLevel] = None
    ) -> bool:
        """Set value in cache"""
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS]
        
        if ttl is None:
            ttl = self.default_ttl
        
        cache_key = self.cache_key(namespace, key)
        success = True
        
        # Set in memory cache
        if CacheLevel.MEMORY in levels:
            success = success and self._set_in_memory(cache_key, value, ttl)
        
        # Set in Redis cache
        if CacheLevel.REDIS in levels:
            success = success and await self._set_in_redis(cache_key, value, ttl)
        
        return success
    
    async def delete(
        self,
        namespace: str,
        key: str,
        levels: List[CacheLevel] = None
    ) -> bool:
        """Delete value from cache"""
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS]
        
        cache_key = self.cache_key(namespace, key)
        success = True
        
        # Delete from memory cache
        if CacheLevel.MEMORY in levels:
            success = success and self._delete_from_memory(cache_key)
        
        # Delete from Redis cache
        if CacheLevel.REDIS in levels:
            success = success and await self._delete_from_redis(cache_key)
        
        return success
    
    async def clear(
        self,
        namespace: str = None,
        levels: List[CacheLevel] = None
    ) -> bool:
        """Clear cache"""
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS]
        
        success = True
        
        # Clear memory cache
        if CacheLevel.MEMORY in levels:
            if namespace:
                prefix = self.cache_key(namespace, "")
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(prefix)]
                for key in keys_to_delete:
                    self._delete_from_memory(key)
            else:
                self.memory_cache.clear()
                self.memory_metadata.clear()
                self.current_memory_size = 0
        
        # Clear Redis cache
        if CacheLevel.REDIS in levels:
            if namespace:
                pattern = self.cache_key(namespace, "*")
                cursor = 0
                while True:
                    cursor, keys = self.redis_client.scan(cursor, match=pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
            else:
                self.redis_client.flushdb()
        
        return success
    
    def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        if key in self.memory_cache:
            metadata = self.memory_metadata.get(key, {})
            
            # Check TTL
            if "expires_at" in metadata:
                if datetime.now() > metadata["expires_at"]:
                    self._delete_from_memory(key)
                    return None
            
            # Update access time for LRU
            metadata["last_accessed"] = datetime.now()
            metadata["access_count"] = metadata.get("access_count", 0) + 1
            self.memory_metadata[key] = metadata
            
            return self.memory_cache[key]
        
        return None
    
    def _set_in_memory(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in memory cache"""
        try:
            # Calculate size
            value_size = len(pickle.dumps(value))
            
            # Check if we need to evict items
            if self.current_memory_size + value_size > self.memory_size_limit:
                self._evict_from_memory(value_size)
            
            # Store value
            self.memory_cache[key] = value
            self.memory_metadata[key] = {
                "size": value_size,
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
                "access_count": 1
            }
            
            if ttl:
                self.memory_metadata[key]["expires_at"] = datetime.now() + timedelta(seconds=ttl)
            
            self.current_memory_size += value_size
            return True
            
        except Exception as e:
            logger.error(f"Error setting memory cache: {e}")
            return False
    
    def _delete_from_memory(self, key: str) -> bool:
        """Delete value from memory cache"""
        if key in self.memory_cache:
            metadata = self.memory_metadata.get(key, {})
            self.current_memory_size -= metadata.get("size", 0)
            del self.memory_cache[key]
            if key in self.memory_metadata:
                del self.memory_metadata[key]
            return True
        return False
    
    def _evict_from_memory(self, required_size: int):
        """Evict items from memory cache using LRU strategy"""
        # Sort by last accessed time (LRU)
        sorted_keys = sorted(
            self.memory_metadata.keys(),
            key=lambda k: self.memory_metadata[k].get("last_accessed", datetime.min)
        )
        
        freed_size = 0
        for key in sorted_keys:
            if freed_size >= required_size:
                break
            
            metadata = self.memory_metadata.get(key, {})
            freed_size += metadata.get("size", 0)
            self._delete_from_memory(key)
            self.cache_stats["evictions"] += 1
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Error getting from Redis: {e}")
        
        return None
    
    async def _set_in_redis(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in Redis cache"""
        try:
            serialized = pickle.dumps(value)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Error setting in Redis: {e}")
            return False
    
    async def _delete_from_redis(self, key: str) -> bool:
        """Delete value from Redis cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting from Redis: {e}")
            return False
    
    def cache_decorator(
        self,
        namespace: str,
        ttl: int = None,
        key_func: Callable = None,
        levels: List[CacheLevel] = None
    ):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self.hash_key({"args": args, "kwargs": kwargs})
                
                # Try to get from cache
                cached_value = await self.get(namespace, cache_key, levels)
                if cached_value is not None:
                    return cached_value
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Store in cache
                await self.set(namespace, cache_key, result, ttl, levels)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self.hash_key({"args": args, "kwargs": kwargs})
                
                # Try to get from cache
                cached_value = asyncio.run(self.get(namespace, cache_key, levels))
                if cached_value is not None:
                    return cached_value
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Store in cache
                asyncio.run(self.set(namespace, cache_key, result, ttl, levels))
                
                return result
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0
        if self.cache_stats["hits"] + self.cache_stats["misses"] > 0:
            hit_rate = self.cache_stats["hits"] / (self.cache_stats["hits"] + self.cache_stats["misses"]) * 100
        
        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "memory_size": self.current_memory_size,
            "memory_size_mb": self.current_memory_size / (1024 * 1024),
            "memory_items": len(self.memory_cache),
            "memory_limit_mb": self.memory_size_limit / (1024 * 1024)
        }
    
    async def warm_cache(self, warmup_data: List[Dict[str, Any]]):
        """Warm up cache with predefined data"""
        for item in warmup_data:
            await self.set(
                namespace=item["namespace"],
                key=item["key"],
                value=item["value"],
                ttl=item.get("ttl"),
                levels=item.get("levels")
            )
    
    async def invalidate_pattern(self, namespace: str, pattern: str):
        """Invalidate cache entries matching a pattern"""
        # Memory cache
        prefix = self.cache_key(namespace, "")
        keys_to_delete = []
        for key in self.memory_cache.keys():
            if key.startswith(prefix) and pattern in key:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self._delete_from_memory(key)
        
        # Redis cache
        redis_pattern = self.cache_key(namespace, f"*{pattern}*")
        cursor = 0
        while True:
            cursor, keys = self.redis_client.scan(cursor, match=redis_pattern)
            if keys:
                self.redis_client.delete(*keys)
            if cursor == 0:
                break

class PageCacheService:
    """Service for caching rendered pages"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    async def get_page(self, url: str, device: str = "desktop") -> Optional[str]:
        """Get cached page HTML"""
        key = f"{url}:{device}"
        return await self.cache.get("pages", key)
    
    async def set_page(
        self,
        url: str,
        html: str,
        device: str = "desktop",
        ttl: int = 3600
    ) -> bool:
        """Cache page HTML"""
        key = f"{url}:{device}"
        return await self.cache.set("pages", key, html, ttl)
    
    async def invalidate_page(self, url: str):
        """Invalidate all versions of a page"""
        for device in ["desktop", "mobile", "tablet"]:
            key = f"{url}:{device}"
            await self.cache.delete("pages", key)
    
    async def invalidate_site(self, site_id: str):
        """Invalidate all pages for a site"""
        await self.cache.invalidate_pattern("pages", site_id)

class APICacheService:
    """Service for caching API responses"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    def cache_endpoint(
        self,
        ttl: int = 300,
        vary_by: List[str] = None,
        invalidate_on: List[str] = None
    ):
        """Decorator for caching API endpoints"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key based on vary_by parameters
                cache_key_parts = [func.__name__]
                
                if vary_by:
                    for param in vary_by:
                        if param in kwargs:
                            cache_key_parts.append(f"{param}:{kwargs[param]}")
                
                cache_key = ":".join(cache_key_parts)
                
                # Try to get from cache
                cached = await self.cache.get("api", cache_key)
                if cached is not None:
                    return cached
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Store in cache
                await self.cache.set("api", cache_key, result, ttl)
                
                return result
            
            return wrapper
        
        return decorator

class QueryCacheService:
    """Service for caching database queries"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    async def get_query_result(
        self,
        query: str,
        params: Dict[str, Any] = None
    ) -> Optional[Any]:
        """Get cached query result"""
        key = self.cache.hash_key({"query": query, "params": params})
        return await self.cache.get("queries", key)
    
    async def set_query_result(
        self,
        query: str,
        result: Any,
        params: Dict[str, Any] = None,
        ttl: int = 300
    ) -> bool:
        """Cache query result"""
        key = self.cache.hash_key({"query": query, "params": params})
        return await self.cache.set("queries", key, result, ttl)
    
    async def invalidate_table(self, table_name: str):
        """Invalidate all queries for a table"""
        await self.cache.invalidate_pattern("queries", table_name)

class AssetCacheService:
    """Service for caching static assets"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    async def get_asset(self, path: str) -> Optional[bytes]:
        """Get cached asset"""
        return await self.cache.get("assets", path)
    
    async def set_asset(
        self,
        path: str,
        content: bytes,
        content_type: str,
        ttl: int = 86400  # 24 hours
    ) -> bool:
        """Cache asset"""
        data = {
            "content": content,
            "content_type": content_type,
            "cached_at": datetime.now().isoformat()
        }
        return await self.cache.set("assets", path, data, ttl)
    
    def get_cache_headers(self, max_age: int = 31536000) -> Dict[str, str]:
        """Get cache control headers for assets"""
        return {
            "Cache-Control": f"public, max-age={max_age}, immutable",
            "Expires": (datetime.now() + timedelta(seconds=max_age)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        }

# Initialize global cache service
cache_service = CacheService()
page_cache = PageCacheService(cache_service)
api_cache = APICacheService(cache_service)
query_cache = QueryCacheService(cache_service)
asset_cache = AssetCacheService(cache_service)