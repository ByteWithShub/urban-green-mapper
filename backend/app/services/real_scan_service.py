import base64
import json
from functools import lru_cache
from io import BytesIO
from urllib.request import urlopen
import asyncio
import httpx
from datetime import datetime, timedelta 
import matplotlib
from PIL import Image
import numpy as np
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import planetary_computer
import rasterio
from pystac_client import Client
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


CITY_CENTER = {
    "Ottawa": (45.4215, -75.6972),
    "Victoria": (48.4284, -123.3656),
    "Edmonton": (53.5461, -113.4938),
    "Regina": (50.4452, -104.6189),
    "Winnipeg": (49.8951, -97.1384),
    "Toronto": (43.6532, -79.3832),
    "Quebec City": (46.8139, -71.2080),
    "Fredericton": (45.9636, -66.6431),
    "Halifax": (44.6488, -63.5752),
    "Charlottetown": (46.2382, -63.1311),
    "St. John's": (47.5615, -52.7126),
    "Whitehorse": (60.7212, -135.0568),
    "Yellowknife": (62.4540, -114.3718),
    "Iqaluit": (63.7467, -68.5170),
}


def make_city_bbox(city: str, half_size: float = 0.08):
    if city not in CITY_CENTER:
        raise ValueError(f"Unsupported city: {city}")

    lat, lon = CITY_CENTER[city]

    return (
        lon - half_size,
        lat - half_size,
        lon + half_size,
        lat + half_size,
    )


CITY_BBOX = {
    city: make_city_bbox(city)
    for city in CITY_CENTER
}


@lru_cache(maxsize=32)
def get_weather(city: str):
    lat, lon = CITY_CENTER.get(city, CITY_CENTER["Ottawa"])

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )

    try:
        with urlopen(url, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            current = data.get("current", {})

            return {
                "temperature_c": current.get("temperature_2m"),
                "humidity_pct": current.get("relative_humidity_2m"),
                "wind_kmh": current.get("wind_speed_10m"),
            }

    except Exception:
        return {
            "temperature_c": None,
            "humidity_pct": None,
            "wind_kmh": None,
        }


def search_scene(lat: float, lon: float):
    import requests

    delta = 0.05
    bbox = [lon - delta, lat - delta, lon + delta, lat + delta]

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=60)

    params = {
        "collections": ["sentinel-2-l2a"],
        "bbox": bbox,
        "datetime": f"{start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "query": {"eo:cloud_cover": {"lt": 20}},
        "sortby": [{"field": "eo:cloud_cover", "direction": "asc"}],
        "limit": 3,
    }

    response = requests.post(
        "https://planetarycomputer.microsoft.com/api/stac/v1/search",
        json=params,
        headers={"Content-Type": "application/json"},
        timeout=25,
    )
    response.raise_for_status()
    features = response.json().get("features", [])

    if not features:
        raise ValueError(f"No Sentinel-2 scenes found for lat={lat}, lon={lon}")

    # Convert raw feature dict to a signed pystac Item
    import pystac
    item = pystac.Item.from_dict(features[0])
    return planetary_computer.sign(item)


@lru_cache(maxsize=32)
def get_cached_scene(city: str):
    lat, lon = CITY_CENTER[city]
    return search_scene(lat, lon)


def read_band(asset_href: str, bbox: list[float], target_size: int = 64) -> np.ndarray:
    """
    Read a single band from a COG asset, windowed to bbox, resampled to target_size.
    Fast: uses overview levels + window read — never reads the full scene.
    """
    import rasterio
    from rasterio.windows import from_bounds
    from rasterio.enums import Resampling
    from rasterio.crs import CRS
    from rasterio.warp import transform_bounds

    env = rasterio.Env(
        GDAL_HTTP_TIMEOUT=15,          # Hard 15s HTTP timeout per tile request
        GDAL_HTTP_MAX_RETRY=1,         # No retries — fail fast
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",  # Skip slow directory scans
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff",
        GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
        GDAL_HTTP_MULTIPLEX="YES",
    )

    with env:
        with rasterio.open(asset_href) as src:
            # Transform bbox from EPSG:4326 → dataset CRS
            dst_crs = src.crs
            west, south, east, north = transform_bounds(
                CRS.from_epsg(4326), dst_crs,
                bbox[0], bbox[1], bbox[2], bbox[3]
            )
            
            window = from_bounds(west, south, east, north, src.transform)
            
            # Read at target_size — rasterio picks the best overview automatically
            data = src.read(
                1,
                window=window,
                out_shape=(target_size, target_size),
                resampling=Resampling.nearest  # Fastest resampling
            )
    
    return data.astype(np.float32)


def normalize_band(band):
    valid = band[band > 0]

    if valid.size == 0:
        return np.zeros_like(band)

    p2, p98 = np.percentile(valid, (2, 98))

    if p98 - p2 == 0:
        return np.zeros_like(band)

    return np.clip((band - p2) / (p98 - p2), 0, 1)


def safe_index(a, b):
    denominator = a + b
    return np.where(denominator == 0, 0, (a - b) / denominator)


def calculate_savi(nir, red, l=0.5):
    denominator = nir + red + l

    return np.where(
        denominator == 0,
        np.nan,
        ((nir - red) / denominator) * (1 + l),
    )


def classify_ndvi(ndvi):
    classes = np.zeros_like(ndvi, dtype="uint8")
    classes[(ndvi >= 0.20) & (ndvi < 0.40)] = 1
    classes[(ndvi >= 0.40) & (ndvi < 0.60)] = 2
    classes[ndvi >= 0.60] = 3
    return classes


def encode_image(arr=None, rgb=None, cmap="viridis", vmin=None, vmax=None):
    fig, ax = plt.subplots(figsize=(9, 6), dpi=150)

    if rgb is not None:
        ax.imshow(rgb)
    else:
        masked = np.ma.masked_invalid(arr)
        ax.imshow(masked, cmap=cmap, vmin=vmin, vmax=vmax)

    ax.axis("off")
    fig.tight_layout(pad=0)

    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


@lru_cache(maxsize=32)
def run_real_scan(city: str, user_type: str, layer_focus: str) -> ScanResponse:
    if city not in CITY_BBOX:
        raise ValueError(f"Unsupported city: {city}")

    bbox = CITY_BBOX[city]
    scene = get_cached_scene(city)

    blue = read_band(scene.assets["B02"].href, bbox=bbox)
    green = read_band(scene.assets["B03"].href, bbox=bbox)
    red = read_band(scene.assets["B04"].href, bbox=bbox)
    nir = read_band(scene.assets["B08"].href, bbox=bbox)
    swir = read_band(scene.assets["B11"].href, bbox=bbox)

    # Resize swir to match red shape
    swir = np.array(
        Image.fromarray(swir).resize(
            (red.shape[1], red.shape[0]), Image.BILINEAR
        )
    )
    
    valid_mask = (red > 0) & (green > 0) & (blue > 0) & (nir > 0)

    rgb = np.dstack(
        [
            normalize_band(red),
            normalize_band(green),
            normalize_band(blue),
        ]
    )

    rgb[~valid_mask] = 0

    ndvi = np.where(valid_mask, safe_index(nir, red), np.nan)
    ndwi = np.where(valid_mask, safe_index(green, nir), np.nan)
    ndbi = np.where(valid_mask, safe_index(swir, nir), np.nan)
    savi = np.where(valid_mask, calculate_savi(nir, red), np.nan)
    classification = classify_ndvi(np.nan_to_num(ndvi, nan=0))
    heat = ndbi - ndvi

    green_pct = float(np.nanmean(ndvi > 0.20) * 100)
    dense_pct = float(np.nanmean(ndvi > 0.60) * 100)
    water_pct = float(np.nanmean(ndwi > 0.05) * 100)
    built_up_pct = float(np.nanmean(ndbi > 0.10) * 100)

    mean_ndvi = float(np.nanmean(ndvi))
    mean_ndwi = float(np.nanmean(ndwi))
    mean_ndbi = float(np.nanmean(ndbi))

    weather = get_weather(city)
    temperature = weather["temperature_c"]

    temp_pressure = 0 if temperature is None else max(0, (temperature - 20) * 1.8)

    heat_risk_score = round(
        min(100, max(0, built_up_pct + (45 - dense_pct) + temp_pressure)),
        1,
    )

    scene_cloud_cover = float(scene.properties.get("eo:cloud_cover", 0))
    reliability_score = round(max(0, 100 - scene_cloud_cover), 1)

    green_pct = round(green_pct, 2)
    dense_pct = round(dense_pct, 2)
    water_pct = round(water_pct, 2)
    built_up_pct = round(built_up_pct, 2)
    mean_ndvi = round(mean_ndvi, 3)
    mean_ndwi = round(mean_ndwi, 3)
    mean_ndbi = round(mean_ndbi, 3)

    return ScanResponse(
        layers=LayerImages(
            rgb=encode_image(rgb=rgb),
            ndvi=encode_image(ndvi, cmap="RdYlGn", vmin=-0.2, vmax=0.8),
            ndwi=encode_image(ndwi, cmap="Blues", vmin=-0.6, vmax=0.6),
            ndbi=encode_image(ndbi, cmap="inferno", vmin=-0.5, vmax=0.5),
            savi=encode_image(savi, cmap="RdYlGn", vmin=-0.2, vmax=0.8),
            classification=encode_image(
                classification,
                cmap="viridis",
                vmin=0,
                vmax=3,
            ),
            heat=encode_image(heat, cmap="magma", vmin=-0.8, vmax=0.8),
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
            resolution="Sentinel-2 bands rendered at 512px production crop",
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