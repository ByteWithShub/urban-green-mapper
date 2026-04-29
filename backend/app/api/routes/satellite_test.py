from fastapi import APIRouter
import traceback

router = APIRouter()


@router.get("/satellite/test")
def test_satellite_connection():
    try:
        import planetary_computer
        from pystac_client import Client

        catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

        bbox = (-76.10, 44.95, -75.25, 45.55)

        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime="2024-07-01/2024-07-10",  # 🔥 small range
            limit=1,  # 🔥 only 1 scene
        )

        items = list(search.items())

        if not items:
            return {
                "connected": True,
                "scene_count": 0,
                "message": "Connected, but no Sentinel-2 scenes found.",
            }

        signed = planetary_computer.sign(items[0])

        return {
            "connected": True,
            "scene_count": len(items),
            "best_scene": {
                "id": signed.id,
                "datetime": str(signed.datetime),
                "cloud_cover": signed.properties.get("eo:cloud_cover"),
                "available_bands": list(signed.assets.keys()),
                "has_rgb_bands": all(band in signed.assets for band in ["B02", "B03", "B04"]),
                "has_ndvi_bands": all(band in signed.assets for band in ["B04", "B08"]),
            },
        }

    except Exception as error:
        return {
            "connected": False,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
        }