from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse
from datetime import datetime
import os

from mars.service.mars_service import get_local_tile_path, get_nasa_tile_url

router = APIRouter()

@router.get("/metadata/mars")
async def get_mars_metadata():
    now = datetime.now().isoformat()
    print(f"[{now}] Mars metadata requested")
    return {
        "planet": "mars",
        "initial_view": {"center": [0, 0], "zoom": 2},
        "title_url_template": "/api/tiles/{dataset}/{z}/{x}/{y}.jpg",
        "available_dataset": ["global"],
        "zoom_range": {"min": 0, "max": 14},
    }

@router.get("/tiles/{dataset}/{z}/{x}/{y}.jpg")
async def get_tile_global(dataset: str, z: int, x: int, y: int):
    now = datetime.now().isoformat()
    
    tile_path = get_local_tile_path(dataset, z, x, y)
    if os.path.exists(tile_path):
        print(f"[{now}] ✓ Served local tile: {tile_path}")
        return FileResponse(tile_path, media_type="image/jpeg")
    
    nasa_url = get_nasa_tile_url(dataset, z, x, y)
    print(f"[{now}] ↗ Redirecting to NASA: {nasa_url}")
    return RedirectResponse(nasa_url, status_code=302)
