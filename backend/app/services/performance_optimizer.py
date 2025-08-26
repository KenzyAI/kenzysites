"""
Performance Optimizer Service
Optimizes site generation to achieve < 45s generation time
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import functools
import cachetools
from dataclasses import dataclass
import redis
import pickle
import hashlib
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for tracking"""
    operation: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    details: Dict[str, Any]

class CacheStrategy:
    """Cache strategies"""
    MEMORY = "memory"
    REDIS = "redis"
    HYBRID = "hybrid"

class PerformanceOptimizer:
    """
    Service for optimizing performance across the site generation pipeline
    """
    
    def __init__(self, cache_strategy: str = CacheStrategy.HYBRID):
        self.cache_strategy = cache_strategy
        self.metrics: List[PerformanceMetrics] = []
        
        # Thread pool for I/O operations
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
        # Process pool for CPU-intensive operations
        self.process_pool = ProcessPoolExecutor(max_workers=4)
        
        # Memory cache
        self.memory_cache = cachetools.TTLCache(maxsize=1000, ttl=3600)
        
        # Redis cache (if available)
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=False
            )
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis cache initialized")
        except:
            self.redis_available = False
            logger.warning("⚠️ Redis not available, using memory cache only")
    
    def measure_performance(self, operation: str):
        """Decorator to measure operation performance"""
        
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                details = {}
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    details["error"] = str(e)
                    raise
                finally:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    metric = PerformanceMetrics(
                        operation=operation,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        success=success,
                        details=details
                    )
                    
                    self.metrics.append(metric)
                    
                    if duration > 5:  # Log slow operations
                        logger.warning(f"⚠️ Slow operation: {operation} took {duration:.2f}s")
                    else:
                        logger.debug(f"✅ {operation} completed in {duration:.2f}s")
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                details = {}
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    details["error"] = str(e)
                    raise
                finally:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    metric = PerformanceMetrics(
                        operation=operation,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        success=success,
                        details=details
                    )
                    
                    self.metrics.append(metric)
                    
                    if duration > 5:
                        logger.warning(f"⚠️ Slow operation: {operation} took {duration:.2f}s")
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    def cached(self, ttl: int = 3600, key_prefix: str = ""):
        """Decorator for caching function results"""
        
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(
                    key_prefix or func.__name__,
                    args,
                    kwargs
                )
                
                # Check cache
                cached_result = await self._get_from_cache(cache_key)
                if cached_result is not None:
                    logger.debug(f"🎯 Cache hit for {cache_key}")
                    return cached_result
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Store in cache
                await self._set_in_cache(cache_key, result, ttl)
                
                return result
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(
                    key_prefix or func.__name__,
                    args,
                    kwargs
                )
                
                # Check cache
                cached_result = self._get_from_cache_sync(cache_key)
                if cached_result is not None:
                    logger.debug(f"🎯 Cache hit for {cache_key}")
                    return cached_result
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Store in cache
                self._set_in_cache_sync(cache_key, result, ttl)
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    async def optimize_template_selection(
        self,
        templates: List[Dict[str, Any]],
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimized template selection using parallel scoring"""
        
        # Score templates in parallel
        scoring_tasks = [
            self._score_template_async(template, criteria)
            for template in templates
        ]
        
        scores = await asyncio.gather(*scoring_tasks)
        
        # Find best template
        best_idx = scores.index(max(scores))
        return templates[best_idx]
    
    async def optimize_ai_calls(
        self,
        ai_tasks: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Any]:
        """Optimize AI API calls with batching and concurrency control"""
        
        # Group tasks by type for batching
        grouped_tasks = {}
        for task in ai_tasks:
            task_type = task.get("type", "default")
            if task_type not in grouped_tasks:
                grouped_tasks[task_type] = []
            grouped_tasks[task_type].append(task)
        
        results = []
        
        # Process each group with concurrency control
        for task_type, tasks in grouped_tasks.items():
            # Create batches
            batch_size = min(max_concurrent, len(tasks))
            batches = [tasks[i:i+batch_size] for i in range(0, len(tasks), batch_size)]
            
            for batch in batches:
                batch_results = await asyncio.gather(*[
                    self._execute_ai_task(task) for task in batch
                ])
                results.extend(batch_results)
        
        return results
    
    async def optimize_image_loading(
        self,
        image_urls: List[str],
        preload: bool = True,
        lazy_load: bool = True
    ) -> Dict[str, Any]:
        """Optimize image loading with preloading and lazy loading strategies"""
        
        optimized_images = []
        
        for url in image_urls:
            # Generate optimized versions
            optimized = {
                "original": url,
                "thumbnail": f"{url}?w=150&q=70",
                "small": f"{url}?w=400&q=80",
                "medium": f"{url}?w=800&q=85",
                "large": f"{url}?w=1200&q=90",
                "lazy_load": lazy_load,
                "preload": preload and image_urls.index(url) < 3  # Preload first 3 images
            }
            optimized_images.append(optimized)
        
        return {
            "images": optimized_images,
            "loading_strategy": "lazy" if lazy_load else "eager",
            "preload_count": sum(1 for img in optimized_images if img["preload"])
        }
    
    async def optimize_database_queries(
        self,
        queries: List[str],
        use_connection_pool: bool = True
    ) -> List[Any]:
        """Optimize database queries with connection pooling and batching"""
        
        # Batch similar queries
        batched_queries = self._batch_queries(queries)
        
        # Execute in parallel with connection pool
        if use_connection_pool:
            results = await asyncio.gather(*[
                self._execute_query_batch(batch)
                for batch in batched_queries
            ])
        else:
            results = []
            for batch in batched_queries:
                batch_result = await self._execute_query_batch(batch)
                results.append(batch_result)
        
        return results
    
    def optimize_content_generation(
        self,
        content_blocks: List[Dict[str, Any]],
        parallel: bool = True
    ) -> List[str]:
        """Optimize content generation with parallel processing"""
        
        if parallel:
            # Use process pool for CPU-intensive content generation
            with self.process_pool as pool:
                results = pool.map(self._generate_content_block, content_blocks)
                return list(results)
        else:
            return [self._generate_content_block(block) for block in content_blocks]
    
    async def optimize_file_operations(
        self,
        file_operations: List[Dict[str, Any]],
        batch_size: int = 10
    ) -> List[bool]:
        """Optimize file operations with batching and async I/O"""
        
        results = []
        
        # Process in batches
        for i in range(0, len(file_operations), batch_size):
            batch = file_operations[i:i+batch_size]
            batch_results = await asyncio.gather(*[
                self._execute_file_operation(op) for op in batch
            ])
            results.extend(batch_results)
        
        return results
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        
        if not self.metrics:
            return {"message": "No metrics collected yet"}
        
        total_duration = sum(m.duration for m in self.metrics)
        successful_ops = sum(1 for m in self.metrics if m.success)
        failed_ops = len(self.metrics) - successful_ops
        
        # Group by operation
        operations = {}
        for metric in self.metrics:
            if metric.operation not in operations:
                operations[metric.operation] = {
                    "count": 0,
                    "total_duration": 0,
                    "avg_duration": 0,
                    "min_duration": float('inf'),
                    "max_duration": 0
                }
            
            op = operations[metric.operation]
            op["count"] += 1
            op["total_duration"] += metric.duration
            op["min_duration"] = min(op["min_duration"], metric.duration)
            op["max_duration"] = max(op["max_duration"], metric.duration)
            op["avg_duration"] = op["total_duration"] / op["count"]
        
        # Find bottlenecks
        bottlenecks = sorted(
            operations.items(),
            key=lambda x: x[1]["total_duration"],
            reverse=True
        )[:5]
        
        return {
            "summary": {
                "total_operations": len(self.metrics),
                "successful_operations": successful_ops,
                "failed_operations": failed_ops,
                "total_duration": total_duration,
                "average_duration": total_duration / len(self.metrics) if self.metrics else 0
            },
            "operations": operations,
            "bottlenecks": dict(bottlenecks),
            "recommendations": self._generate_recommendations(operations, total_duration)
        }
    
    def _generate_recommendations(
        self,
        operations: Dict[str, Any],
        total_duration: float
    ) -> List[str]:
        """Generate performance improvement recommendations"""
        
        recommendations = []
        
        # Check if total duration exceeds target
        if total_duration > 45:
            recommendations.append(
                f"⚠️ Total generation time ({total_duration:.1f}s) exceeds target of 45s"
            )
        
        # Check for slow operations
        for op_name, op_stats in operations.items():
            if op_stats["avg_duration"] > 5:
                recommendations.append(
                    f"🔧 Optimize '{op_name}' - average duration {op_stats['avg_duration']:.2f}s"
                )
        
        # Check cache hit rate
        cache_ops = [m for m in self.metrics if "cache" in m.operation.lower()]
        if cache_ops:
            hit_rate = sum(1 for m in cache_ops if "hit" in str(m.details)) / len(cache_ops)
            if hit_rate < 0.5:
                recommendations.append(
                    f"📊 Low cache hit rate ({hit_rate:.1%}) - consider increasing cache TTL"
                )
        
        # Suggest parallelization
        sequential_ops = [op for op in operations if operations[op]["count"] > 3]
        if sequential_ops:
            recommendations.append(
                f"⚡ Consider parallelizing operations: {', '.join(sequential_ops)}"
            )
        
        if not recommendations:
            recommendations.append("✅ Performance is within acceptable limits")
        
        return recommendations
    
    async def _score_template_async(
        self,
        template: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> float:
        """Score a template asynchronously"""
        
        await asyncio.sleep(0)  # Yield control
        
        score = 0.0
        
        # Industry match
        if template.get("industry") == criteria.get("industry"):
            score += 30
        
        # Feature match
        template_features = set(template.get("features", []))
        required_features = set(criteria.get("features", []))
        feature_match = len(template_features & required_features) / max(len(required_features), 1)
        score += feature_match * 20
        
        # Complexity match
        if template.get("complexity") == criteria.get("complexity"):
            score += 10
        
        # Rating
        score += template.get("rating", 0) * 5
        
        return score
    
    async def _execute_ai_task(self, task: Dict[str, Any]) -> Any:
        """Execute an AI task"""
        
        # Simulate AI API call
        await asyncio.sleep(0.5)
        return {"result": f"AI result for {task.get('type', 'unknown')}"}
    
    def _batch_queries(self, queries: List[str]) -> List[List[str]]:
        """Batch similar queries together"""
        
        batches = []
        current_batch = []
        
        for query in queries:
            # Simple batching by query type (SELECT, INSERT, UPDATE, etc.)
            query_type = query.strip().split()[0].upper()
            
            if current_batch and current_batch[0].strip().split()[0].upper() != query_type:
                batches.append(current_batch)
                current_batch = [query]
            else:
                current_batch.append(query)
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    async def _execute_query_batch(self, batch: List[str]) -> List[Any]:
        """Execute a batch of queries"""
        
        # Simulate database query execution
        await asyncio.sleep(0.1 * len(batch))
        return [f"Result for query {i}" for i in range(len(batch))]
    
    def _generate_content_block(self, block: Dict[str, Any]) -> str:
        """Generate a content block"""
        
        # Simulate content generation
        time.sleep(0.1)
        return f"Generated content for {block.get('type', 'unknown')}"
    
    async def _execute_file_operation(self, operation: Dict[str, Any]) -> bool:
        """Execute a file operation"""
        
        # Simulate file operation
        await asyncio.sleep(0.05)
        return True
    
    def _generate_cache_key(self, prefix: str, args: tuple, kwargs: dict) -> str:
        """Generate a cache key from function arguments"""
        
        # Create a string representation of arguments
        key_parts = [prefix]
        
        # Add args
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            elif isinstance(arg, (list, tuple, dict)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(type(arg)))
        
        # Add kwargs
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}={v}")
            elif isinstance(v, (list, tuple, dict)):
                key_parts.append(f"{k}={json.dumps(v, sort_keys=True)}")
            else:
                key_parts.append(f"{k}={type(v)}")
        
        # Generate hash
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache (async)"""
        
        # Try memory cache first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Try Redis if available
        if self.redis_available and self.cache_strategy in [CacheStrategy.REDIS, CacheStrategy.HYBRID]:
            try:
                value = self.redis_client.get(key)
                if value:
                    deserialized = pickle.loads(value)
                    # Store in memory cache for faster access
                    if self.cache_strategy == CacheStrategy.HYBRID:
                        self.memory_cache[key] = deserialized
                    return deserialized
            except Exception as e:
                logger.error(f"Redis get error: {str(e)}")
        
        return None
    
    def _get_from_cache_sync(self, key: str) -> Optional[Any]:
        """Get value from cache (sync)"""
        
        # Try memory cache first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Try Redis if available
        if self.redis_available and self.cache_strategy in [CacheStrategy.REDIS, CacheStrategy.HYBRID]:
            try:
                value = self.redis_client.get(key)
                if value:
                    deserialized = pickle.loads(value)
                    # Store in memory cache for faster access
                    if self.cache_strategy == CacheStrategy.HYBRID:
                        self.memory_cache[key] = deserialized
                    return deserialized
            except Exception as e:
                logger.error(f"Redis get error: {str(e)}")
        
        return None
    
    async def _set_in_cache(self, key: str, value: Any, ttl: int):
        """Set value in cache (async)"""
        
        # Store in memory cache
        if self.cache_strategy in [CacheStrategy.MEMORY, CacheStrategy.HYBRID]:
            self.memory_cache[key] = value
        
        # Store in Redis if available
        if self.redis_available and self.cache_strategy in [CacheStrategy.REDIS, CacheStrategy.HYBRID]:
            try:
                serialized = pickle.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
            except Exception as e:
                logger.error(f"Redis set error: {str(e)}")
    
    def _set_in_cache_sync(self, key: str, value: Any, ttl: int):
        """Set value in cache (sync)"""
        
        # Store in memory cache
        if self.cache_strategy in [CacheStrategy.MEMORY, CacheStrategy.HYBRID]:
            self.memory_cache[key] = value
        
        # Store in Redis if available
        if self.redis_available and self.cache_strategy in [CacheStrategy.REDIS, CacheStrategy.HYBRID]:
            try:
                serialized = pickle.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
            except Exception as e:
                logger.error(f"Redis set error: {str(e)}")
    
    def clear_cache(self):
        """Clear all caches"""
        
        self.memory_cache.clear()
        
        if self.redis_available:
            try:
                self.redis_client.flushdb()
                logger.info("✅ Cache cleared")
            except Exception as e:
                logger.error(f"Error clearing Redis cache: {str(e)}")
    
    def __del__(self):
        """Cleanup on deletion"""
        
        self.thread_pool.shutdown(wait=False)
        self.process_pool.shutdown(wait=False)

# Create singleton instance
performance_optimizer = PerformanceOptimizer()