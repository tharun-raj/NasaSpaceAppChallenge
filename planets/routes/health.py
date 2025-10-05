from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Server health check"""
    now = datetime.now().isoformat()
    print(f"[{now}] Health check requested")
    return {"status": "healthy", "timestamp": now}