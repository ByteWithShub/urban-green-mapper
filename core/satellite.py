import numpy as np
import pandas as pd
import planetary_computer
import rasterio
from pystac_client import Client
from rasterio.enums import Resampling


def search_sentinel2(
    bbox,
    start_date,
    end_date,
    max_cloud_cover=20,
    limit=20,
) -> pd.DataFrame:
    catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=f"{start_date}/{end_date}",
        query={"eo:cloud_cover": {"lt": max_cloud_cover}},
        limit=limit,
    )

    rows = []

    for item in search.items():
        signed = planetary_computer.sign(item)

        rows.append({
            "id": signed.id,
            "datetime": signed.datetime,
            "cloud_cover": signed.properties.get("eo:cloud_cover"),
            "platform": signed.properties.get("platform"),
            "B02": signed.assets["B02"].href if "B02" in signed.assets else None,
            "B03": signed.assets["B03"].href if "B03" in signed.assets else None,
            "B04": signed.assets["B04"].href if "B04" in signed.assets else None,
            "B08": signed.assets["B08"].href if "B08" in signed.assets else None,
            "B11": signed.assets["B11"].href if "B11" in signed.assets else None,
        })

    return pd.DataFrame(rows).sort_values("cloud_cover")


def read_band(url: str, scale_factor: int = 8, target_shape: tuple | None = None) -> np.ndarray:
    with rasterio.open(url) as src:
        if target_shape is None:
            out_shape = (
                max(1, src.height // scale_factor),
                max(1, src.width // scale_factor),
            )
        else:
            out_shape = target_shape

        band = src.read(
            1,
            out_shape=out_shape,
            resampling=Resampling.bilinear,
        ).astype("float32")

    return band


def normalize_band(band: np.ndarray) -> np.ndarray:
    valid = band[band > 0]

    if valid.size == 0:
        return np.zeros_like(band)

    p2, p98 = np.percentile(valid, (2, 98))

    if p98 - p2 == 0:
        return np.zeros_like(band)

    return np.clip((band - p2) / (p98 - p2), 0, 1)


def make_rgb(red, green, blue):
    return np.dstack([
        normalize_band(red),
        normalize_band(green),
        normalize_band(blue),
    ])


def summarize_classes(classified: np.ndarray) -> pd.DataFrame:
    labels = {
        0: "Non-green / Built-up / Water / Bare",
        1: "Low vegetation",
        2: "Moderate vegetation",
        3: "Dense vegetation",
    }

    total = classified.size
    rows = []

    for class_id, label in labels.items():
        count = int(np.sum(classified == class_id))
        rows.append({
            "class_id": class_id,
            "class_name": label,
            "pixel_count": count,
            "percentage": round((count / total) * 100, 2),
        })

    return pd.DataFrame(rows)