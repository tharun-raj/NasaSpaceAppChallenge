import asyncio
from io import BytesIO
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from datetime import datetime
import os

from planets.cache.tile_cache import (
    cache_tile_data, 
    get_cached_tile_data, 
    get_neighboring_tiles,
)
from planets.service.mars_service import get_nasa_tile_url
from service.image_service import fetch_data_from_url

router = APIRouter()

PREFETCH_SEMAPHORE = asyncio.Semaphore(5)

recent_prefetch_requests = {}

@router.get("/metadata/planets")
async def get_mars_metadata():
    now = datetime.now().isoformat()
    print(f"[{now}] Mars metadata requested")
    return {
        "planet": "mars",
        "initial_view": {"center": [0, 0], "zoom": 2},
        "title_url_template": "/api/tiles/{dataset}/{z}/{x}/{y}.jpg",
        "available_dataset": ["global", "moon"],
        "zoom_range": {"min": 0, "max": 7},
    }


async def smart_prefetch_with_limit(dataset: str, z: int, x: int, y: int, fetch_func):
    key = f"{dataset}:{z}:{x}:{y}"
    
    if key in recent_prefetch_requests:
        return
    
    recent_prefetch_requests[key] = True
    
    if len(recent_prefetch_requests) > 1000:
        recent_prefetch_requests.clear()
    
    async with PREFETCH_SEMAPHORE:
        neighbors = get_neighboring_tiles(z, x, y, radius=1)
        
        tasks = []
        for tz, tx, ty in neighbors[:8]:
            neighbor_key = f"{dataset}:{tz}:{tx}:{ty}"
            if neighbor_key not in recent_prefetch_requests:
                tasks.append(prefetch_single_tile_limited(dataset, tz, tx, ty, fetch_func))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    await asyncio.sleep(2)
    recent_prefetch_requests.pop(key, None)


async def prefetch_single_tile_limited(dataset: str, z: int, x: int, y: int, fetch_func):
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


@router.get("/tiles/{dataset}/{z}/{x}/{y}.jpg")
async def get_tile_global(z: int, x: int, y: int, dataset: str = "global"):
    cached_data = await get_cached_tile_data(dataset, z, x, y)
    if cached_data:
        asyncio.create_task(
            smart_prefetch_with_limit(dataset, z, x, y, fetch_data_from_url)
        )
        
        return StreamingResponse(
            BytesIO(cached_data),
            media_type="image/jpeg",
            headers={
                "X-Cache": "HIT", 
                "Cache-Control": "public, max-age=86400",
                "Access-Control-Expose-Headers": "X-Cache"
            }
        )
    
    nasa_url = get_nasa_tile_url(z, x, y, dataset)
    print(nasa_url)
    data = await fetch_data_from_url(nasa_url)
    
    if data:
        asyncio.create_task(cache_tile_data(dataset, z, x, y, data))
        
        asyncio.create_task(
            smart_prefetch_with_limit(dataset, z, x, y, fetch_data_from_url)
        )
        
        return StreamingResponse(
            BytesIO(data),
            media_type="image/jpeg",
            headers={
                "X-Cache": "MISS", 
                "Cache-Control": "public, max-age=86400",
                "Access-Control-Expose-Headers": "X-Cache"
            }
        )
    
    return {"error": "Could not fetch tile"}, 404