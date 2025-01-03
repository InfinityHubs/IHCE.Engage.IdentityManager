from fastapi import APIRouter, Depends
from src.app.services.health_check import liveness, readiness

router = APIRouter(prefix="/health", tags=["Health"])

# Health check routes
@router.get("/liveness", include_in_schema=False)
async def health_check_liveness(liveness_status: bool = Depends(liveness)):
    return liveness_status

@router.get("/readiness", include_in_schema=False)
async def health_check_readiness(readiness_status: bool = Depends(readiness)):
    return readiness_status
