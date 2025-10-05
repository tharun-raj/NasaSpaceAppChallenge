import asyncio
from typing import Optional
import redis.asyncio as aioredis
from redis.exceptions import RedisError
from cachetools import TTLCache
import threading

from planets.service.mars_service import get_nasa_tile_url

# Use async Redis client with connection pooling
redis_client: Optional[aioredis.Redis] = None

# In-memory LRU cache for hot tiles (faster than Redis)
# This acts as L1 cache, Redis is L2 cache
memory_cache = TTLCache(maxsize=500, ttl=300)  # 500 tiles, 5 min TTL
cache_lock = threading.Lock()

# Cache statistics
cache_stats = {
    "memory_hits": 0,
    "memory_misses": 0,
    "redis_hits": 0,
    "redis_misses": 0,
    "total_requests": 0
}

async def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=False,
            socket_connect_timeout=1,
            socket_timeout=1,
            max_connections=50,
            health_check_interval=30
        )
    return redis_client


def get_cache_key(dataset: str, z: int, x: int, y: int) -> str:
    return f"tile:{dataset}:{z}:{x}:{y}"


async def get_cached_tile_data(dataset: str, z: int, x: int, y: int) -> Optional[bytes]:
    """Two-tier cache: memory (L1) -> Redis (L2)"""
    key = get_cache_key(dataset, z, x, y)
    
    cache_stats["total_requests"] += 1
    
    # Check memory cache first (fastest)
    with cache_lock:
        if key in memory_cache:
            cache_stats["memory_hits"] += 1
            return memory_cache[key]
    
    cache_stats["memory_misses"] += 1
    
    # Check Redis cache
    try:
        client = await get_redis_client()
        data = await client.get(key)
        
        if data:
            cache_stats["redis_hits"] += 1
            # Promote to memory cache
            with cache_lock:
                memory_cache[key] = data
            return data
        
        cache_stats["redis_misses"] += 1
        return None
    except RedisError:
        cache_stats["redis_misses"] += 1
        return None


async def cache_tile_data(dataset: str, z: int, x: int, y: int, data: bytes, ttl: int = 86400) -> bool:
    """Cache to both memory and Redis"""
    key = get_cache_key(dataset, z, x, y)
    
    # Store in memory cache
    with cache_lock:
        memory_cache[key] = data
    
    # Store in Redis
    try:
        client = await get_redis_client()
        await client.setex(key, ttl, data)
        return True
    except RedisError:
        return False


async def batch_get_tiles(dataset: str, tiles: list) -> dict:
    """Efficiently fetch multiple tiles at once using Redis pipeline"""
    try:
        client = await get_redis_client()
        pipe = client.pipeline()
        
        keys = [get_cache_key(dataset, z, x, y) for z, x, y in tiles]
        
        for key in keys:
            pipe.get(key)
        
        results = await pipe.execute()
        
        tile_data = {}
        for (z, x, y), data in zip(tiles, results):
            if data:
                tile_data[(z, x, y)] = data
        
        return tile_data
    except RedisError:
        return {}


async def batch_cache_tiles(dataset: str, tile_data: dict, ttl: int = 86400) -> int:
    """Efficiently cache multiple tiles at once using Redis pipeline"""
    try:
        client = await get_redis_client()
        pipe = client.pipeline()
        
        count = 0
        for (z, x, y), data in tile_data.items():
            key = get_cache_key(dataset, z, x, y)
            pipe.setex(key, ttl, data)
            count += 1
        
        await pipe.execute()
        return count
    except RedisError:
        return 0


async def get_cache_stats() -> dict:
    """Get comprehensive cache statistics"""
    stats = cache_stats.copy()
    
    # Memory cache stats
    with cache_lock:
        stats["memory_cache_size"] = len(memory_cache)
        stats["memory_cache_maxsize"] = memory_cache.maxsize
    
    # Redis stats
    try:
        client = await get_redis_client()
        redis_info = await client.info('stats')
        redis_memory = await client.info('memory')
        
        stats["redis_hits_total"] = redis_info.get("keyspace_hits", 0)
        stats["redis_misses_total"] = redis_info.get("keyspace_misses", 0)
        stats["redis_memory_used"] = redis_memory.get("used_memory_human", "N/A")
        stats["redis_connected_clients"] = redis_info.get("connected_clients", 0)
        
        # Calculate hit rates
        total_memory = stats["memory_hits"] + stats["memory_misses"]
        if total_memory > 0:
            stats["memory_hit_rate"] = f"{(stats['memory_hits'] / total_memory * 100):.2f}%"
        
        total_redis = stats["redis_hits"] + stats["redis_misses"]
        if total_redis > 0:
            stats["redis_hit_rate"] = f"{(stats['redis_hits'] / total_redis * 100):.2f}%"
        
        # Overall hit rate
        total_hits = stats["memory_hits"] + stats["redis_hits"]
        if stats["total_requests"] > 0:
            stats["overall_hit_rate"] = f"{(total_hits / stats['total_requests'] * 100):.2f}%"
        
    except RedisError as e:
        stats["redis_error"] = str(e)
    
    return stats


async def clear_cache(dataset: Optional[str] = None, z: Optional[int] = None):
    """Clear cache - useful for maintenance"""
    # Clear memory cache
    with cache_lock:
        if dataset and z is not None:
            # Clear specific zoom level
            keys_to_remove = [k for k in memory_cache.keys() if f"tile:{dataset}:{z}:" in k]
            for key in keys_to_remove:
                del memory_cache[key]
        else:
            memory_cache.clear()
    
    # Clear Redis cache
    try:
        client = await get_redis_client()
        if dataset and z is not None:
            pattern = f"tile:{dataset}:{z}:*"
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
        elif dataset:
            pattern = f"tile:{dataset}:*"
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
        else:
            await client.flushdb()
    except RedisError:
        pass


def get_neighboring_tiles(z: int, x: int, y: int, radius: int = 1) -> list:
    """Get neighboring tiles with wrap-around for global map"""
    tiles = []
    
    num_cols = 2 * (2 ** z)
    num_rows = 1 * (2 ** z)
    
    x = x % num_cols
    y = max(0, min(y, num_rows - 1))
    
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx == 0 and dy == 0:
                continue
            
            new_x = (x + dx) % num_cols
            new_y = y + dy
            
            if 0 <= new_y < num_rows:
                tiles.append((z, new_x, new_y))
    
    return tiles


async def prefetch_single_tile(dataset: str, z: int, x: int, y: int, fetch_func) -> bool:
    """Prefetch a single tile silently"""
    try:
        if await get_cached_tile_data(dataset, z, x, y):
            return True
        
        nasa_url = get_nasa_tile_url(z, x, y, dataset)
        data = await fetch_func(nasa_url)
        
        if data:
            await cache_tile_data(dataset, z, x, y, data)
            return True
        return False
    except Exception:
        return False


async def smart_prefetch_neighbors(
    dataset: str,
    z: int,
    x: int,
    y: int,
    fetch_func,
    radius: int = 1,
    zoom_radius: int = 0,
    max_zoom: int = 7,
):
    """Optimized prefetch - only same zoom level by default"""
    if z > max_zoom:
        return
    
    neighbors = get_neighboring_tiles(z, x, y, radius)
    cached = await batch_get_tiles(dataset, neighbors)
    
    tasks = []
    for tz, tx, ty in neighbors:
        if (tz, tx, ty) not in cached:
            tasks.append(prefetch_single_tile(dataset, tz, tx, ty, fetch_func))
    
    if tasks:
        for i in range(0, len(tasks), 4):
            batch = tasks[i:i+4]
            await asyncio.gather(*batch, return_exceptions=True)
            await asyncio.sleep(0.01)