def answer_question(question: str, context: dict) -> str:
    q = question.lower()

    city = context.get("city", "this location")
    green_pct = context.get("green_pct", 0)
    dense_pct = context.get("dense_pct", 0)
    mean_ndvi = context.get("mean_ndvi", 0)
    heat_label = context.get("heat_label", "unknown")
    quality_label = context.get("quality_label", "unknown")

    if "ndvi" in q:
        return (
            "NDVI stands for Normalized Difference Vegetation Index. "
            "It uses red and near-infrared satellite bands to estimate vegetation health. "
            f"For {city}, the mean NDVI is {mean_ndvi:.3f}."
        )

    if "water" in q or "ndwi" in q:
        return (
            "Water is better explored using NDWI. NDWI compares green and near-infrared bands. "
            "Higher NDWI values may indicate water bodies or moisture-rich surfaces."
        )

    if "built" in q or "urban" in q or "ndbi" in q:
        return (
            "Built-up areas can be explored using NDBI. It compares SWIR and NIR bands. "
            "Higher values often suggest roads, rooftops, concrete, or dense urban surfaces."
        )

    if "reliable" in q or "quality" in q or "cloud" in q:
        return (
            f"The current scene quality is rated {quality_label}. "
            "Cloud cover affects reliability because clouds and shadows can hide land features."
        )

    if "heat" in q or "risk" in q:
        return (
            f"The current heat-risk estimate for {city} is {heat_label}. "
            "This score is based on vegetation coverage, dense canopy, and weather conditions."
        )

    if "green" in q or "vegetation" in q:
        return (
            f"{city} has approximately {green_pct:.2f}% green coverage, "
            f"with {dense_pct:.2f}% dense vegetation in the selected satellite scene."
        )

    if "kid" in q or "simple" in q:
        return (
            "Satellites can see plant light that our eyes cannot see. "
            "Healthy plants bounce back invisible light, so we use that signal to find green areas."
        )

    if "limitation" in q:
        return (
            "Main limitations include cloud cover, shadows, seasonality, mixed pixels, "
            "resolution limits, and the fact that satellite indices estimate surface patterns rather than exact ground truth."
        )

    return (
        "I can help explain NDVI, water, built-up areas, heat risk, image reliability, "
        "green coverage, and limitations. Try asking: 'What does NDVI mean?' or 'Is this image reliable?'"
    )