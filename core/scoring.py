def quality_score(cloud_cover: float) -> tuple[int, str]:
    score = max(0, min(100, round(100 - cloud_cover)))

    if score >= 90:
        label = "Excellent"
    elif score >= 75:
        label = "Good"
    elif score >= 55:
        label = "Usable"
    else:
        label = "Cloudy / weak reliability"

    return score, label


def heat_risk_score(green_pct: float, dense_pct: float, temperature: float | None) -> tuple[int, str]:
    temp_component = 0 if temperature is None else max(0, min(40, (temperature - 20) * 2))
    vegetation_component = max(0, 45 - green_pct)
    canopy_component = max(0, 25 - dense_pct)

    score = round(min(100, temp_component + vegetation_component + canopy_component))

    if score >= 70:
        label = "High"
    elif score >= 40:
        label = "Moderate"
    else:
        label = "Low"

    return score, label