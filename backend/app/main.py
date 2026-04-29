from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.satellite_test import router as satellite_test_router
from app.api.routes.health import router as health_router
from app.api.routes.scan import router as scan_router
from app.api.routes.chat import router as chat_router
from app.core.config import settings

app = FastAPI(
    title="EarthLens API",
    description="Urban Green Space Intelligence Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TEMP for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(satellite_test_router, prefix="/api", tags=["Satellite Test"])
app.include_router(health_router, tags=["Health"])
app.include_router(scan_router, prefix="/api", tags=["Scan"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])