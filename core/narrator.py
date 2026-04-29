def explain_for_audience(
    audience: str,
    city: str,
    mean_ndvi: float,
    green_pct: float,
    dense_pct: float,
    heat_label: str,
    quality_label: str,
) -> str:
    if audience == "Kid Explorer":
        return f"""
### Green Detective Brief

We scanned **{city}** from space!

Plants reflect invisible light that satellites can see. When the number is high, it usually means more healthy green stuff like trees, grass, and parks.

- Green coverage: **{green_pct:.2f}%**
- Super leafy areas: **{dense_pct:.2f}%**
- Heat risk: **{heat_label}**
- Image quality: **{quality_label}**

If this city were a creature, its green spaces would be its lungs. 🌿
"""

    if audience == "City Planner":
        return f"""
### Planning Brief

The selected Sentinel-2 scene for **{city}** shows **{green_pct:.2f}%** estimated vegetation coverage and **{dense_pct:.2f}%** dense vegetation.

This can support early screening for:
- tree canopy gaps
- heat-risk corridors
- park access concerns
- priority areas for greening investment

Image reliability is currently rated **{quality_label}**.
"""

    if audience == "Climate Scientist":
        return f"""
### Climate/Remote Sensing Brief

The scene has a mean NDVI of **{mean_ndvi:.3f}**, with **{green_pct:.2f}%** of pixels classified above the vegetation threshold.

Dense vegetation accounts for **{dense_pct:.2f}%** of the analyzed area. Combined with the heat-risk estimate of **{heat_label}**, this suggests a preliminary proxy for urban thermal vulnerability.

Further work should include atmospheric-quality filtering, seasonal time-series baselines, and neighborhood-level overlay analysis.
"""

    if audience == "AI Researcher":
        return f"""
### AI Research Brief

This pipeline converts multispectral Sentinel-2 bands into interpretable environmental features.

Current feature layer:
- mean NDVI: **{mean_ndvi:.3f}**
- green coverage: **{green_pct:.2f}%**
- dense vegetation: **{dense_pct:.2f}%**
- heat risk label: **{heat_label}**
- scene quality: **{quality_label}**

Potential ML extensions:
- temporal vegetation forecasting
- segmentation model training
- anomaly detection on seasonal NDVI
- multimodal fusion with weather and census features
"""

    return f"""
### Student Brief

For **{city}**, the satellite image shows **{green_pct:.2f}%** green coverage. NDVI helps measure vegetation because healthy plants reflect near-infrared light strongly and absorb red light.

The scene quality is **{quality_label}**, and the estimated heat risk is **{heat_label}**.
"""