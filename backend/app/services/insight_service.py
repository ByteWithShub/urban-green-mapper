def generate_brief(
    city: str,
    user_type: str,
    green_pct: float,
    dense_pct: float,
    water_pct: float,
    built_up_pct: float,
    mean_ndvi: float,
    heat_risk_score: float,
    reliability_score: float,
) -> str:
    user_type = user_type.lower()

    if user_type in ["kids", "kid", "child"]:
        return (
            f"{city} has a pretty visible green signal from space. "
            f"About {green_pct}% of the area looks green, and {dense_pct}% looks like thick tree or plant cover. "
            f"The satellite also sees water-like areas and city surfaces. Think of NDVI as a plant-health thermometer."
        )

    if user_type in ["researcher", "expert", "phd", "scientist"]:
        return (
            f"EarthLens mock analysis for {city} reports mean NDVI={mean_ndvi}, "
            f"green coverage={green_pct}%, dense vegetation={dense_pct}%, "
            f"water-associated signal={water_pct}%, and built-up signal={built_up_pct}%. "
            f"The derived heat-risk score is {heat_risk_score}/100, with reliability estimated at "
            f"{reliability_score}/100 under the current mock scene assumptions. "
            f"In the real Sentinel-2 phase, interpretation should account for cloud contamination, "
            f"seasonality, mixed pixels, atmospheric correction, and spatial resolution limits."
        )

    if user_type in ["planner", "weather", "city_planner", "environment"]:
        return (
            f"{city} shows {green_pct}% total green coverage and {dense_pct}% dense vegetation. "
            f"Built-up signal is estimated at {built_up_pct}%, while heat-risk pressure is {heat_risk_score}/100. "
            f"This can support urban cooling, tree-canopy planning, stormwater awareness, and climate adaptation discussions."
        )

    return (
        f"EarthLens scanned {city} and found {green_pct}% green coverage, "
        f"{dense_pct}% dense vegetation, and a mean NDVI of {mean_ndvi}. "
        f"The current heat-risk score is {heat_risk_score}/100."
    )


def generate_research_notes() -> list[str]:
    return [
        "NDVI is useful for vegetation signal, but it can saturate in dense canopy.",
        "NDWI helps highlight water or moisture-associated features.",
        "NDBI can indicate built-up surfaces, but confusion may occur with bare soil.",
        "SAVI is useful where soil brightness affects vegetation interpretation.",
        "Future real-data mode should include cloud masking, date selection, and Sentinel-2 scene metadata.",
    ]


def generate_kid_summary(city: str, green_pct: float) -> str:
    return (
        f"From space, {city} looks about {green_pct}% green in this demo scan. "
        f"Satellites can see plant glow that our eyes cannot see."
    )