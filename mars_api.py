from datetime import datetime
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

app = FastAPI()

@app.get("/api/health")
async def health_check():
    """Server health check"""
    now = datetime.now().isoformat()
    print(f"[{now}] Health check requested")
    return {"status": "healthy", "timestamp": now}

@app.get("/api/metadata/mars")
async def get_mars_metadata():
    now = datetime.now().isoformat()
    print(f"[{now}] Mars metadata requested")
    return {
        "planet": "mars",
        "initial_view": {
            "center": [0, 0],
            "zoom": 2
        },
        "title_url_template": "/api/title/{dataset}/{data}/{z}/{x}/{y}.jpg",
        "available_dataset": ["global"],
        "zoom_range": {"min": 0, "max": 14}
    }

@app.get("/api/tiles/{dataset}/{z}/{x}/{y}.jpg")
async def get_tile_global(dataset: str, z: int, x: int, y: int):
    now = datetime.now().isoformat()
    
    # Check local cache first
    tile_path = f"tiles/{dataset}/latest/{z}/{y}/{x}.jpg"  
    
    if os.path.exists(tile_path):
        print(f"[{now}] ✓ Served local tile: {tile_path}")
        return FileResponse(tile_path, media_type="image/jpeg")
    
    # NASA Trek URL format: z/row/col (which is z/y/x)
    nasa_url = (
        f"https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/"
        f"default/default028mm/{z}/{y}/{x}.jpg"
    )
    print(f"[{now}] ↗ Redirecting to NASA: {nasa_url}")
    return RedirectResponse(nasa_url, status_code=302)