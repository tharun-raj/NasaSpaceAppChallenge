from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List

from ai.gemini_analyzer import MarsImageAnalyzer
from planets.cache.tile_cache import get_cached_tile_data
from planets.service.mars_service import get_nasa_tile_url
from service.image_service import fetch_data_from_url

router = APIRouter(prefix="/ai", tags=["AI Analysis"])

analyzer = MarsImageAnalyzer()

class TileAnalysisRequest(BaseModel):
    dataset: str = Field(default="global", description="Dataset name (e.g., 'global')")
    z: int = Field(..., ge=0, le=14, description="Zoom level (0-14)")
    x: int = Field(..., ge=0, description="Tile X coordinate")
    y: int = Field(..., ge=0, description="Tile Y coordinate")
    question: str = Field(..., min_length=1, description="Question about the Mars surface")

class GeneralAnalysisRequest(BaseModel):
    dataset: str = Field(default="global")
    z: int = Field(..., ge=0, le=14)
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)

class FeatureDetectionRequest(BaseModel):
    dataset: str = Field(default="global")
    z: int = Field(..., ge=0, le=14)
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)
    features: List[str] = Field(..., description="Features to detect (e.g., ['craters', 'rocks', 'dunes'])")

class TileComparisonRequest(BaseModel):
    tile1: dict = Field(..., description="First tile: {dataset, z, x, y}")
    tile2: dict = Field(..., description="Second tile: {dataset, z, x, y}")

class AnalysisResponse(BaseModel):
    status: str
    analysis: str
    tile_info: dict
    cache_status: str

class ComparisonResponse(BaseModel):
    status: str
    comparison: str
    tile1_info: dict
    tile2_info: dict


async def fetch_tile_image(dataset: str, z: int, x: int, y: int) -> bytes:
    cached_data = await get_cached_tile_data(dataset, z, x, y)
    if cached_data:
        return cached_data
    
    # Fetch from NASA
    nasa_url = get_nasa_tile_url(z, x, y, dataset)
    data = await fetch_data_from_url(nasa_url)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"Could not fetch tile: {dataset}/{z}/{x}/{y}"
        )
    
    return data


@router.post("/analyze-tile", response_model=AnalysisResponse)
async def analyze_mars_tile(request: TileAnalysisRequest):
    try:
        image_data = await fetch_tile_image(request.dataset, request.z, request.x, request.y)
        
        cache_status = "HIT" if await get_cached_tile_data(
            request.dataset, request.z, request.x, request.y
        ) else "MISS"
        
        tile_info = {
            "dataset": request.dataset,
            "z": request.z,
            "x": request.x,
            "y": request.y
        }
        
        analysis = await analyzer.analyze_mars_tile(
            image_data=image_data,
            question=request.question,
            tile_info=tile_info
        )
        
        return AnalysisResponse(
            status="success",
            analysis=analysis,
            tile_info=tile_info,
            cache_status=cache_status
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/analyze-features", response_model=AnalysisResponse)
async def analyze_general_features(request: GeneralAnalysisRequest):
    try:
        image_data = await fetch_tile_image(request.dataset, request.z, request.x, request.y)
        
        cache_status = "HIT" if await get_cached_tile_data(
            request.dataset, request.z, request.x, request.y
        ) else "MISS"
        
        analysis = await analyzer.analyze_general_features(image_data)
        
        tile_info = {
            "dataset": request.dataset,
            "z": request.z,
            "x": request.x,
            "y": request.y
        }
        
        return AnalysisResponse(
            status="success",
            analysis=analysis,
            tile_info=tile_info,
            cache_status=cache_status
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Feature analysis failed: {str(e)}"
        )


@router.post("/detect-features", response_model=AnalysisResponse)
async def detect_specific_features(request: FeatureDetectionRequest):
    try:
        if not request.features:
            raise HTTPException(status_code=400, detail="No features specified")
        
        image_data = await fetch_tile_image(request.dataset, request.z, request.x, request.y)
        
        cache_status = "HIT" if await get_cached_tile_data(
            request.dataset, request.z, request.x, request.y
        ) else "MISS"
        
        analysis = await analyzer.detect_specific_features(image_data, request.features)
        
        tile_info = {
            "dataset": request.dataset,
            "z": request.z,
            "x": request.x,
            "y": request.y,
            "features_searched": request.features
        }
        
        return AnalysisResponse(
            status="success",
            analysis=analysis,
            tile_info=tile_info,
            cache_status=cache_status
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Feature detection failed: {str(e)}"
        )


@router.post("/compare-tiles", response_model=ComparisonResponse)
async def compare_mars_tiles(request: TileComparisonRequest):
    try:
        tile1 = request.tile1
        tile2 = request.tile2
        
        required_keys = ['dataset', 'z', 'x', 'y']
        for tile, name in [(tile1, 'tile1'), (tile2, 'tile2')]:
            if not all(k in tile for k in required_keys):
                raise HTTPException(
                    status_code=400,
                    detail=f"{name} missing required keys: {required_keys}"
                )
        
        image1_data = await fetch_tile_image(
            tile1['dataset'], tile1['z'], tile1['x'], tile1['y']
        )
        image2_data = await fetch_tile_image(
            tile2['dataset'], tile2['z'], tile2['x'], tile2['y']
        )
        
        comparison = await analyzer.compare_tiles(
            image1_data=image1_data,
            image2_data=image2_data,
            tile1_info=tile1,
            tile2_info=tile2
        )
        
        return ComparisonResponse(
            status="success",
            comparison=comparison,
            tile1_info=tile1,
            tile2_info=tile2
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )


@router.get("/analyze", response_model=AnalysisResponse)
async def analyze_tile_get(
    dataset: str = Query(default="global"),
    z: int = Query(..., ge=0, le=14),
    x: int = Query(..., ge=0),
    y: int = Query(..., ge=0),
    question: str = Query(..., min_length=1)
):
    request = TileAnalysisRequest(
        dataset=dataset,
        z=z,
        x=x,
        y=y,
        question=question
    )
    return await analyze_mars_tile(request)