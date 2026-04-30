import base64
import json
from datetime import datetime, timedelta
from functools import lru_cache
from io import BytesIO
from urllib.request import urlopen

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import planetary_computer
import pystac
import rasterio
import requests
from PIL import Image
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

from app.schemas.scan import (
    LayerImages,
    ScanMetadata,
    ScanMetrics,
    ScanResponse,
)
from app.services.insight_service import (
    generate_brief,
    generate_kid_summary,
    generate_research_notes,
)


# ---------------------------------------------------------------------------
# City centre coordinates
# ---------------------------------------------------------------------------

CITY_CENTER = {
    "Ottawa":        (45.4215,  -75.6972),
    "Victoria":      (48.4284, -123.3656),
    "Edmonton":      (53.5461, -113.4938),
    "Regina":        (50.4452, -104.6189),
    "Winnipeg":      (49.8951,  -97.1384),
    "Toronto":       (43.6532,  -79.3832),
    "Quebec City":   (46.8139,  -71.2080),
    "Fredericton":   (45.9636,  -66.6431),
    "Halifax":       (44.6488,  -63.5752),
    "Charlottetown": (46.2382,  -63.1311),
    "St. John's":    (47.5615,  -52.7126),
    "Whitehorse":    (60.7212, -135.0568),
    "Yellowknife":   (62.4540, -114.3718),
    "Iqaluit":       (63.7467,  -68.5170),
}

# Bounding box half-size in degrees (~8 km radius — wide enough for context,
# small enough to keep Planetary Computer response times fast on Render Free).
_HALF = 0.08

CITY_BBOX = {
    city: (lon - _HALF, lat - _HALF, lon + _HALF, lat + _HALF)
    for city, (lat, lon) in CITY_CENTER.items()
}

# Output raster size for all 10 m bands.  512 gives crisp, HD-quality images
# while keeping memory and network load manageable on Render Free tier.
BAND_SIZE = 512


# ---------------------------------------------------------------------------
# Weather helper
# ---------------------------------------------------------------------------

@lru_cache(maxsize=32)
def get_weather(city: str) -> dict:
    lat, lon = CITY_CENTER.get(city, CITY_CENTER["Ottawa"])
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    try:
        with urlopen(url, timeout=8) as resp:
            current = json.loads(resp.read().decode()).get("current", {})
            return {
                "temperature_c": current.get("temperature_2m"),
                "humidity_pct":  current.get("relative_humidity_2m"),
                "wind_kmh":      current.get("wind_speed_10m"),
            }
    except Exception:
        return {"temperature_c": None, "humidity_pct": None, "wind_kmh": None}


# ---------------------------------------------------------------------------
# Scene search  (sync, uses requests — no async complexity on Render)
# ---------------------------------------------------------------------------

def search_scene(lat: float, lon: float):
    """
    Query Planetary Computer STAC for the best recent, low-cloud Sentinel-2
    scene centred on (lat, lon).  Uses a small 0.10° bbox so the API responds
    quickly.  Falls back to a wider 60-day / 45 % cloud window if needed.
    """
    delta = 0.05  # ~5 km radius
    bbox  = [lon - delta, lat - delta, lon + delta, lat + delta]

    search_configs = [
        (30,  20),   # last 30 days, <20 % cloud
        (60,  35),   # last 60 days, <35 % cloud
        (120, 60),   # last 120 days, <60 % cloud
    ]

    last_exc = None
    for days, cloud_limit in search_configs:
        try:
            end_dt   = datetime.utcnow()
            start_dt = end_dt - timedelta(days=days)
            params = {
                "collections": ["sentinel-2-l2a"],
                "bbox":        bbox,
                "datetime":    (
                    f"{start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}/"
                    f"{end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}"
                ),
                "query":   {"eo:cloud_cover": {"lt": cloud_limit}},
                "sortby":  [{"field": "eo:cloud_cover", "direction": "asc"}],
                "limit":   5,
            }
            resp = requests.post(
                "https://planetarycomputer.microsoft.com/api/stac/v1/search",
                json=params,
                headers={"Content-Type": "application/json"},
                timeout=25,
            )
            resp.raise_for_status()
            features = resp.json().get("features", [])
            if features:
                item = pystac.Item.from_dict(features[0])
                return planetary_computer.sign(item)
        except Exception as exc:
            last_exc = exc
            print(f"[search_scene] attempt failed (days={days}, cloud<{cloud_limit}%): {exc}")

    raise ValueError(
        f"No Sentinel-2 scene found for lat={lat:.4f}, lon={lon:.4f}. "
        f"Last error: {last_exc}"
    )


@lru_cache(maxsize=32)
def get_cached_scene(city: str):
    lat, lon = CITY_CENTER[city]
    return search_scene(lat, lon)


# ---------------------------------------------------------------------------
# Band reader  (windowed COG read — never pulls the whole scene)
# ---------------------------------------------------------------------------

def read_band(asset_href: str, bbox: tuple, target_size: int = BAND_SIZE) -> np.ndarray:
    """
    Read one Sentinel-2 band from a Cloud-Optimised GeoTIFF.

    • Window-reads only the bbox area   → fast, low-memory
    • out_shape forces rasterio to use  → the best overview level automatically
    • bilinear resampling               → smooth, HD-quality output
    • boundless + fill_value=0          → no crop errors at tile edges
    • GDAL env vars                     → aggressive timeout so Render never hangs
    """
    env = rasterio.Env(
        GDAL_HTTP_TIMEOUT="20",
        GDAL_HTTP_CONNECTTIMEOUT="10",
        GDAL_HTTP_MAX_RETRY="1",
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF",
        GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
        GDAL_HTTP_MULTIPLEX="YES",
    )
    with env:
        with rasterio.open(asset_href) as src:
            west, south, east, north = transform_bounds(
                CRS.from_epsg(4326), src.crs,
                bbox[0], bbox[1], bbox[2], bbox[3],
                densify_pts=21,
            )
            window = from_bounds(west, south, east, north, src.transform)
            window = window.round_offsets().round_lengths()

            data = src.read(
                1,
                window=window,
                out_shape=(target_size, target_size),
                resampling=Resampling.bilinear,
                boundless=True,
                fill_value=0,
            )
    return data.astype(np.float32)


def _resize_to(arr: np.ndarray, h: int, w: int) -> np.ndarray:
    """Resize a 2-D float32 array to (h, w) using bilinear interpolation."""
    pil = Image.fromarray(arr)
    pil = pil.resize((w, h), Image.BILINEAR)
    return np.array(pil, dtype=np.float32)


# ---------------------------------------------------------------------------
# Spectral maths helpers
# ---------------------------------------------------------------------------

def normalize_band(band: np.ndarray) -> np.ndarray:
    valid = band[band > 0]
    if valid.size == 0:
        return np.zeros_like(band)
    p2, p98 = np.percentile(valid, (2, 98))
    if p98 <= p2:
        return np.zeros_like(band)
    return np.clip((band - p2) / (p98 - p2), 0, 1)


def safe_index(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    denom = a + b
    return np.where(denom == 0, 0.0, (a - b) / denom)


def calculate_savi(nir: np.ndarray, red: np.ndarray, l: float = 0.5) -> np.ndarray:
    denom = nir + red + l
    return np.where(denom == 0, np.nan, ((nir - red) / denom) * (1 + l))


def classify_ndvi(ndvi: np.ndarray) -> np.ndarray:
    classes = np.zeros_like(ndvi, dtype="uint8")
    classes[(ndvi >= 0.20) & (ndvi < 0.40)] = 1
    classes[(ndvi >= 0.40) & (ndvi < 0.60)] = 2
    classes[ndvi >= 0.60]                    = 3
    return classes


# ---------------------------------------------------------------------------
# Image encoder  — HD, square, no border, no whitespace
# ---------------------------------------------------------------------------

def encode_image(
    arr=None,
    rgb=None,
    cmap: str = "viridis",
    vmin=None,
    vmax=None,
) -> str:
    """
    Render a numpy array (or RGB stack) to a base64-encoded PNG.

    dpi=150 + figsize=(8,8) → 1200×1200 px output: crisp on retina screens.
    bbox_inches='tight' + pad_inches=0 → zero whitespace / cropping.
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)

    if rgb is not None:
        # Clip to valid display range just in case
        ax.imshow(np.clip(rgb, 0, 1), interpolation="bilinear")
    else:
        masked = np.ma.masked_invalid(arr)
        ax.imshow(
            masked,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            interpolation="bilinear",
        )

    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, dpi=150)
    plt.close(fig)

    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()


# ---------------------------------------------------------------------------
# Main scan entry point
# ---------------------------------------------------------------------------

@lru_cache(maxsize=32)
def run_real_scan(city: str, user_type: str, layer_focus: str) -> ScanResponse:
    if city not in CITY_BBOX:
        raise ValueError(f"Unsupported city: {city}")

    bbox  = CITY_BBOX[city]
    scene = get_cached_scene(city)

    # -- Read all 10 m bands at BAND_SIZE × BAND_SIZE -----------------------
    blue  = read_band(scene.assets["B02"].href, bbox=bbox)
    green = read_band(scene.assets["B03"].href, bbox=bbox)
    red   = read_band(scene.assets["B04"].href, bbox=bbox)
    nir   = read_band(scene.assets["B08"].href, bbox=bbox)

    # B11 (SWIR) is 20 m native res — read at BAND_SIZE then resize to match
    swir_raw = read_band(scene.assets["B11"].href, bbox=bbox, target_size=BAND_SIZE)
    swir = _resize_to(swir_raw, red.shape[0], red.shape[1])

    # -- Valid-pixel mask (exclude no-data edges) ----------------------------
    valid_mask = (red > 0) & (green > 0) & (blue > 0) & (nir > 0)

    # -- RGB composite -------------------------------------------------------
    rgb = np.dstack([
        normalize_band(red),
        normalize_band(green),
        normalize_band(blue),
    ])
    rgb[~valid_mask] = 0.0

    # -- Spectral indices ----------------------------------------------------
    ndvi           = np.where(valid_mask, safe_index(nir, red),   np.nan)
    ndwi           = np.where(valid_mask, safe_index(green, nir), np.nan)
    ndbi           = np.where(valid_mask, safe_index(swir, nir),  np.nan)
    savi           = np.where(valid_mask, calculate_savi(nir, red), np.nan)
    classification = classify_ndvi(np.nan_to_num(ndvi, nan=0.0))
    heat           = ndbi - ndvi  # urban heat proxy

    # -- Metrics -------------------------------------------------------------
    green_pct    = float(np.nanmean(ndvi  >  0.20) * 100)
    dense_pct    = float(np.nanmean(ndvi  >  0.60) * 100)
    water_pct    = float(np.nanmean(ndwi  >  0.05) * 100)
    built_up_pct = float(np.nanmean(ndbi  >  0.10) * 100)
    mean_ndvi    = float(np.nanmean(ndvi))
    mean_ndwi    = float(np.nanmean(ndwi))
    mean_ndbi    = float(np.nanmean(ndbi))

    weather     = get_weather(city)
    temperature = weather["temperature_c"]
    temp_pressure = 0.0 if temperature is None else max(0.0, (temperature - 20) * 1.8)

    heat_risk_score   = round(min(100, max(0, built_up_pct + (45 - dense_pct) + temp_pressure)), 1)
    scene_cloud_cover = float(scene.properties.get("eo:cloud_cover", 0))
    reliability_score = round(max(0, 100 - scene_cloud_cover), 1)

    green_pct    = round(green_pct,    2)
    dense_pct    = round(dense_pct,    2)
    water_pct    = round(water_pct,    2)
    built_up_pct = round(built_up_pct, 2)
    mean_ndvi    = round(mean_ndvi,    3)
    mean_ndwi    = round(mean_ndwi,    3)
    mean_ndbi    = round(mean_ndbi,    3)

    # -- Build response ------------------------------------------------------
    return ScanResponse(
        layers=LayerImages(
            rgb=encode_image(rgb=rgb),
            ndvi=encode_image(ndvi,           cmap="RdYlGn", vmin=-0.2, vmax=0.8),
            ndwi=encode_image(ndwi,           cmap="Blues",  vmin=-0.6, vmax=0.6),
            ndbi=encode_image(ndbi,           cmap="inferno",vmin=-0.5, vmax=0.5),
            savi=encode_image(savi,           cmap="RdYlGn", vmin=-0.2, vmax=0.8),
            classification=encode_image(classification, cmap="viridis", vmin=0, vmax=3),
            heat=encode_image(heat,           cmap="magma",  vmin=-0.8, vmax=0.8),
        ),
        metrics=ScanMetrics(
            green_pct=green_pct,
            dense_pct=dense_pct,
            water_pct=water_pct,
            built_up_pct=built_up_pct,
            mean_ndvi=mean_ndvi,
            mean_ndwi=mean_ndwi,
            mean_ndbi=mean_ndbi,
            heat_risk_score=heat_risk_score,
            reliability_score=reliability_score,
            temperature_c=weather["temperature_c"],
            humidity_pct=weather["humidity_pct"],
            wind_kmh=weather["wind_kmh"],
        ),
        metadata=ScanMetadata(
            city=city,
            cloud_cover=round(scene_cloud_cover, 2),
            date=str(scene.datetime),
            satellite="Sentinel-2 L2A",
            resolution="10 m — 512 px crop, bilinear resampled",
            mode=layer_focus,
        ),
        brief=generate_brief(
            city=city,
            user_type=user_type,
            green_pct=green_pct,
            dense_pct=dense_pct,
            water_pct=water_pct,
            built_up_pct=built_up_pct,
            mean_ndvi=mean_ndvi,
            heat_risk_score=heat_risk_score,
            reliability_score=reliability_score,
        ),
        research_notes=generate_research_notes(),
        kid_summary=generate_kid_summary(city, green_pct),
    )
