"""
Redis Cache Service
Provides caching functionality for improving performance
"""

import redis
import json
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import asyncio
from functools import wraps
import pickle

logger = logging.getLogger(__name__)

class RedisCache:
    """
    Redis-based caching service for KenzySites
    """
    
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection failed: {e}. Falling back to in-memory cache.")
            self.redis_client = None
            self._memory_cache = {}
    
    def _generate_key(self, prefix: str, data: Dict[str, Any]) -> str:
        """Generate a unique cache key from data"""
        # Create a hash of the data for consistent keys
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Fallback to memory cache
                return self._memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (Time To Live) in seconds"""
        try:
            if self.redis_client:
                return self.redis_client.setex(
                    key, 
                    ttl, 
                    json.dumps(value, default=str)
                )
            else:
                # Fallback to memory cache
                self._memory_cache[key] = value
                # Simple TTL simulation (not perfect but works for development)
                asyncio.create_task(self._expire_memory_key(key, ttl))
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def _expire_memory_key(self, key: str, ttl: int):
        """Remove key from memory cache after TTL"""
        await asyncio.sleep(ttl)
        self._memory_cache.pop(key, None)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                return self._memory_cache.pop(key, None) is not None
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                return key in self._memory_cache
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # Memory cache pattern clearing
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern.replace('*', '') in k]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                return len(keys_to_delete)
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', '0B'),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': self._calculate_hit_rate(info.get('keyspace_hits', 0), info.get('keyspace_misses', 0))
                }
            else:
                return {
                    'cache_type': 'memory',
                    'total_keys': len(self._memory_cache),
                    'hit_rate': 'N/A'
                }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {'error': str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> str:
        """Calculate cache hit rate"""
        total = hits + misses
        if total == 0:
            return "0%"
        return f"{(hits / total * 100):.1f}%"


class CacheManager:
    """
    High-level cache manager for specific KenzySites operations
    """
    
    def __init__(self):
        self.cache = RedisCache()
    
    # Template Generation Cache
    def cache_template_generation(self, business_data: Dict[str, Any], result: Dict[str, Any], ttl: int = 7200) -> bool:
        """Cache template generation result"""
        key = self.cache._generate_key('template_gen', business_data)
        result_with_meta = {
            **result,
            'cached_at': datetime.now().isoformat(),
            'ttl': ttl
        }
        return self.cache.set(key, result_with_meta, ttl)
    
    def get_cached_template_generation(self, business_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached template generation"""
        key = self.cache._generate_key('template_gen', business_data)
        return self.cache.get(key)
    
    # Variation Generation Cache
    def cache_variations(self, template_id: str, variations: List[Dict[str, Any]], ttl: int = 3600) -> bool:
        """Cache generated variations"""
        key = f"variations:{template_id}"
        return self.cache.set(key, {
            'variations': variations,
            'generated_at': datetime.now().isoformat(),
            'count': len(variations)
        }, ttl)
    
    def get_cached_variations(self, template_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached variations"""
        key = f"variations:{template_id}"
        cached = self.cache.get(key)
        return cached.get('variations') if cached else None
    
    # AI Response Cache
    def cache_ai_response(self, prompt_hash: str, response: str, ttl: int = 86400) -> bool:
        """Cache AI responses to avoid repeated API calls"""
        key = f"ai_response:{prompt_hash}"
        return self.cache.set(key, {
            'response': response,
            'cached_at': datetime.now().isoformat()
        }, ttl)
    
    def get_cached_ai_response(self, prompt: str) -> Optional[str]:
        """Get cached AI response"""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        key = f"ai_response:{prompt_hash}"
        cached = self.cache.get(key)
        return cached.get('response') if cached else None
    
    # WordPress Templates Cache
    def cache_wp_templates(self, industry: str, templates: List[Dict[str, Any]], ttl: int = 43200) -> bool:
        """Cache WordPress templates by industry"""
        key = f"wp_templates:{industry}"
        return self.cache.set(key, {
            'templates': templates,
            'cached_at': datetime.now().isoformat(),
            'industry': industry
        }, ttl)
    
    def get_cached_wp_templates(self, industry: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached WordPress templates"""
        key = f"wp_templates:{industry}"
        cached = self.cache.get(key)
        return cached.get('templates') if cached else None
    
    # User Session Cache
    def cache_user_session(self, session_id: str, data: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache user session data"""
        key = f"session:{session_id}"
        return self.cache.set(key, data, ttl)
    
    def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data"""
        key = f"session:{session_id}"
        return self.cache.get(key)
    
    # Generation Queue Cache
    def cache_generation_progress(self, generation_id: str, progress: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache generation progress for real-time updates"""
        key = f"generation_progress:{generation_id}"
        progress_data = {
            **progress,
            'updated_at': datetime.now().isoformat()
        }
        return self.cache.set(key, progress_data, ttl)
    
    def get_generation_progress(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """Get generation progress"""
        key = f"generation_progress:{generation_id}"
        return self.cache.get(key)
    
    # Performance Metrics Cache
    def cache_performance_metrics(self, metrics: Dict[str, Any], ttl: int = 300) -> bool:
        """Cache system performance metrics"""
        key = "performance_metrics"
        return self.cache.set(key, {
            **metrics,
            'timestamp': datetime.now().isoformat()
        }, ttl)
    
    def get_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """Get cached performance metrics"""
        key = "performance_metrics"
        return self.cache.get(key)
    
    # Cleanup methods
    def clear_expired_cache(self) -> Dict[str, int]:
        """Clear expired cache entries"""
        cleared = {}
        
        patterns = [
            'template_gen:*',
            'variations:*',
            'ai_response:*',
            'wp_templates:*',
            'session:*',
            'generation_progress:*'
        ]
        
        for pattern in patterns:
            count = self.cache.clear_pattern(pattern)
            cleared[pattern] = count
        
        return cleared
    
    def get_cache_summary(self) -> Dict[str, Any]:
        """Get comprehensive cache summary"""
        stats = self.cache.get_stats()
        
        # Count keys by type
        key_counts = {}
        try:
            if self.cache.redis_client:
                all_keys = self.cache.redis_client.keys('*')
                for key in all_keys:
                    prefix = key.split(':')[0] if ':' in key else 'unknown'
                    key_counts[prefix] = key_counts.get(prefix, 0) + 1
            else:
                for key in self.cache._memory_cache.keys():
                    prefix = key.split(':')[0] if ':' in key else 'unknown'
                    key_counts[prefix] = key_counts.get(prefix, 0) + 1
        except Exception as e:
            logger.error(f"Error counting keys: {e}")
        
        return {
            'stats': stats,
            'key_counts': key_counts,
            'total_keys': sum(key_counts.values()),
            'cache_status': 'redis' if self.cache.redis_client else 'memory'
        }


def cache_result(cache_key_prefix: str, ttl: int = 3600):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache manager instance
            cache_mgr = CacheManager()
            
            # Generate cache key from function arguments
            cache_data = {'args': args, 'kwargs': kwargs}
            cache_key = cache_mgr.cache._generate_key(cache_key_prefix, cache_data)
            
            # Try to get from cache first
            cached_result = cache_mgr.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.info(f"Cache miss for {func.__name__}, executing function")
            result = await func(*args, **kwargs)
            
            # Cache the result
            cache_mgr.cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# Create global cache manager instance
cache_manager = CacheManager()