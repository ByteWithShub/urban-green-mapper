from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import RootResponse, HealthResponse

router = APIRouter()


@router.get("/", response_model=RootResponse)
def root():
    return RootResponse(
        message="EarthLens API is running",
        status="online",
        version=settings.API_VERSION,
    )


@router.get("/api/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        service="EarthLens Backend",
    )