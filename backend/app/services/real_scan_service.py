import base64
import json
from functools import lru_cache
from io import BytesIO
from urllib.request import urlopen

import matplotlib

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


CITY_BBOX = {
    "Ottawa": (-76.15, 45.15, -75.30, 45.65),
    "Victoria": (-123.75, 48.20, -123.10, 48.70),
    "Edmonton": (-114.00, 53.25, -113.05, 53.85),
    "Regina": (-105.00, 50.25, -104.25, 50.70),
    "Winnipeg": (-97.65, 49.60, -96.55, 50.20),
    "Toronto": (-79.95, 43.35, -78.95, 44.05),
    "Quebec City": (-71.85, 46.55, -70.85, 47.10),
    "Fredericton": (-67.05, 45.75, -66.35, 46.20),
    "Halifax": (-64.00, 44.35, -63.20, 44.95),
    "Charlottetown": (-63.45, 46.05, -62.85, 46.45),
    "St. John's": (-53.10, 47.35, -52.40, 47.80),
    "Whitehorse": (-135.55, 60.45, -134.65, 61.00),
    "Yellowknife": (-114.85, 62.25, -113.95, 62.75),
    "Iqaluit": (-69.00, 63.55, -68.15, 64.00),
}

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


def get_valid_pixel_ratio(item, bbox):
    try:
        signed_item = planetary_computer.sign(item)
        red_url = signed_item.assets["B04"].href

        with rasterio.open(red_url) as src:
            projected_bounds = transform_bounds(
                "EPSG:4326",
                src.crs,
                *bbox,
                densify_pts=21,
            )

            window = from_bounds(*projected_bounds, transform=src.transform)
            window = window.round_offsets().round_lengths()

            sample = src.read(
                1,
                window=window,
                out_shape=(160, 160),
                resampling=Resampling.bilinear,
                boundless=True,
                fill_value=0,
            )

            return float(np.mean(sample > 0))

    except Exception:
        return 0.0


def search_scene(city: str):
    if city not in CITY_BBOX:
        raise ValueError(f"Unsupported city: {city}")

    bbox = CITY_BBOX[city]
    catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

    search_configs = [
        ("2024-08-01/2024-09-15", 40),
        ("2024-07-01/2024-10-15", 55),
        ("2023-07-01/2023-10-15", 65),
    ]

    for date_range, cloud_limit in search_configs:
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=date_range,
            query={"eo:cloud_cover": {"lt": cloud_limit}},
            limit=5,
            max_items=5,
        )

        items = list(search.items())

        if items:
            best_item = sorted(
                items,
                key=lambda item: (
                    item.properties.get("eo:cloud_cover", 999),
                    -item.datetime.timestamp(),
                ),
            )[0]

            return planetary_computer.sign(best_item)

    raise ValueError(f"No Sentinel-2 scene found for {city}")


@lru_cache(maxsize=32)
def get_cached_scene(city: str):
    return search_scene(city)


def read_band(url: str, bbox, scale_factor: int = 3, target_shape=None):
    with rasterio.open(url) as src:
        projected_bounds = transform_bounds(
            "EPSG:4326",
            src.crs,
            *bbox,
            densify_pts=21,
        )

        window = from_bounds(*projected_bounds, transform=src.transform)
        window = window.round_offsets().round_lengths()

        if target_shape is None:
            out_shape = (
                max(300, int(window.height // scale_factor)),
                max(300, int(window.width // scale_factor)),
            )
        else:
            out_shape = target_shape

        return src.read(
            1,
            window=window,
            out_shape=out_shape,
            resampling=Resampling.bilinear,
            boundless=False,
        ).astype("float32")


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
    swir = read_band(scene.assets["B11"].href, bbox=bbox, target_shape=red.shape)

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
            resolution="10m / 20m bands cropped to city extent",
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