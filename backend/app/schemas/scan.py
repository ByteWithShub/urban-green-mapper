from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    city: str = Field(default="Ottawa")
    user_type: str = Field(default="researcher")
    layer_focus: str = Field(default="ndvi")


class LayerImages(BaseModel):
    rgb: str
    ndvi: str
    ndwi: str
    ndbi: str
    savi: str
    classification: str
    heat: str


class ScanMetrics(BaseModel):
    green_pct: float
    dense_pct: float
    water_pct: float
    built_up_pct: float
    mean_ndvi: float
    mean_ndwi: float
    mean_ndbi: float
    heat_risk_score: float
    reliability_score: float
    temperature_c: float | None = None
    humidity_pct: float | None = None
    wind_kmh: float | None = None


class ScanMetadata(BaseModel):
    city: str
    cloud_cover: float
    date: str
    satellite: str
    resolution: str
    mode: str


class ScanResponse(BaseModel):
    layers: LayerImages
    metrics: ScanMetrics
    metadata: ScanMetadata
    brief: str
    research_notes: list[str]
    kid_summary: str