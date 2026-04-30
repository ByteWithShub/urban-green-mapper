from functools import lru_cache

from fastapi import APIRouter, HTTPException

from app.schemas.scan import ScanRequest, ScanResponse
from app.services.real_scan_service import run_real_scan

try:
    from app.services.mock_scan_service import run_mock_scan
except Exception:
    run_mock_scan = None


router = APIRouter()


@lru_cache(maxsize=64)
def cached_real_scan(city: str, user_type: str, layer_focus: str):
    return run_real_scan(
        city=city,
        user_type=user_type,
        layer_focus=layer_focus,
    )


@router.post("/scan", response_model=ScanResponse)
def scan_city(payload: ScanRequest):
    try:
        return cached_real_scan(
            city=payload.city,
            user_type=payload.user_type,
            layer_focus=payload.layer_focus,
        )

    except Exception as error:
        print(f"REAL SCAN FAILED: {error}")

        if run_mock_scan is not None:
            return run_mock_scan(
                city=payload.city,
                user_type=payload.user_type,
                layer_focus=payload.layer_focus,
            )

        raise HTTPException(
            status_code=500,
            detail=f"EarthLens scan failed: {str(error)}",
        )