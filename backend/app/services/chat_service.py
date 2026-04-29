def generate_chat_answer(
    message: str,
    city: str,
    user_type: str,
    green_pct: float | None = None,
    dense_pct: float | None = None,
    mean_ndvi: float | None = None,
) -> str:
    msg = message.lower()
    user_type = user_type.lower()

    if "ndvi" in msg:
        if user_type in ["kids", "kid", "child"]:
            return (
                "NDVI is like a plant-health meter. Healthy plants bounce back invisible light, "
                "and satellites can measure that glow."
            )

        return (
            "NDVI stands for Normalized Difference Vegetation Index. "
            "It compares near-infrared and red reflectance to estimate vegetation health and density."
        )

    if "ndwi" in msg or "water" in msg:
        return (
            "NDWI stands for Normalized Difference Water Index. "
            "It helps highlight water bodies and moisture-related surfaces in satellite imagery."
        )

    if "ndbi" in msg or "built" in msg or "urban" in msg:
        return (
            "NDBI stands for Normalized Difference Built-up Index. "
            "It helps identify built-up surfaces such as roads, rooftops, concrete, and dense urban fabric."
        )

    if "savi" in msg:
        return (
            "SAVI stands for Soil Adjusted Vegetation Index. "
            "It improves vegetation estimation in areas where exposed soil affects the satellite signal."
        )

    if "heat" in msg or "risk" in msg:
        if green_pct is not None and dense_pct is not None:
            return (
                f"For {city}, heat-risk interpretation would combine vegetation coverage, dense canopy, "
                f"built-up signal, and later weather data. Current green coverage is {green_pct}% "
                f"with {dense_pct}% dense vegetation."
            )

        return (
            "Urban heat risk can be estimated by combining low vegetation, high built-up surfaces, "
            "limited tree canopy, and weather data such as temperature and humidity."
        )

    if "kid" in msg or user_type in ["kids", "kid", "child"]:
        return (
            f"EarthLens looks at {city} from space and explains where plants, water, and buildings are. "
            f"It turns satellite data into a friendly green-city story."
        )

    if "research" in msg or "limitation" in msg or "reliable" in msg:
        return (
            "Scientific reliability depends on cloud cover, season, sensor resolution, atmospheric correction, "
            "scene date, mixed pixels, and threshold choices. The real-data phase should expose these as metadata."
        )

    return (
        f"Ask EarthLens about NDVI, NDWI, NDBI, SAVI, green coverage, heat risk, water signal, "
        f"urban surfaces, reliability, or how {city} could improve its green infrastructure."
    )