from urllib.parse import quote
import base64 

from app.schemas.scan import (
    ScanResponse,
    LayerImages,
    ScanMetrics,
    ScanMetadata,
)
from app.services.insight_service import (
    generate_brief,
    generate_research_notes,
    generate_kid_summary,
)


def svg_layer(title: str, theme: str) -> str:
    palettes = {
        "rgb": {
            "bg": "#06121f",
            "a": "#35ff9b",
            "b": "#00c2ff",
            "c": "#a7ff5f",
        },
        "ndvi": {
            "bg": "#07150d",
            "a": "#a7ff5f",
            "b": "#39ff88",
            "c": "#e6ff6a",
        },
        "ndwi": {
            "bg": "#04101f",
            "a": "#00d9ff",
            "b": "#3d7bff",
            "c": "#89f7ff",
        },
        "ndbi": {
            "bg": "#15080a",
            "a": "#ff7a3d",
            "b": "#ffcc66",
            "c": "#ff4d6d",
        },
        "savi": {
            "bg": "#101507",
            "a": "#d4ff5f",
            "b": "#75ff9a",
            "c": "#ffe97a",
        },
        "classification": {
            "bg": "#05080d",
            "a": "#2fff8a",
            "b": "#00d9ff",
            "c": "#ff8c42",
        },
    }

    p = palettes.get(theme, palettes["rgb"])

    svg = f"""
    <svg width="1200" height="760" viewBox="0 0 1200 760" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="g1" cx="35%" cy="30%" r="55%">
          <stop offset="0%" stop-color="{p['a']}" stop-opacity="0.75"/>
          <stop offset="55%" stop-color="{p['b']}" stop-opacity="0.30"/>
          <stop offset="100%" stop-color="{p['bg']}" stop-opacity="1"/>
        </radialGradient>

        <filter id="blur">
          <feGaussianBlur stdDeviation="18"/>
        </filter>

        <pattern id="grid" width="70" height="70" patternUnits="userSpaceOnUse">
          <path d="M 70 0 L 0 0 0 70" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
        </pattern>
      </defs>

      <rect width="1200" height="760" fill="{p['bg']}"/>
      <rect width="1200" height="760" fill="url(#grid)"/>

      <path d="M0 540 C180 455 290 620 455 520 C620 420 710 465 875 380 C1000 315 1110 335 1200 285 L1200 760 L0 760 Z"
            fill="{p['a']}" opacity="0.42" filter="url(#blur)"/>

      <path d="M0 250 C160 180 250 280 390 225 C535 168 650 210 780 150 C940 75 1060 110 1200 60"
            stroke="{p['b']}" stroke-width="52" opacity="0.28" fill="none" filter="url(#blur)"/>

      <circle cx="280" cy="250" r="125" fill="{p['a']}" opacity="0.48" filter="url(#blur)"/>
      <circle cx="820" cy="470" r="150" fill="{p['c']}" opacity="0.34" filter="url(#blur)"/>
      <circle cx="990" cy="235" r="90" fill="{p['b']}" opacity="0.38" filter="url(#blur)"/>

      <rect x="46" y="46" width="355" height="64" rx="20" fill="rgba(0,0,0,0.42)" stroke="rgba(255,255,255,0.18)"/>
      <text x="72" y="87" fill="#effff7" font-size="28" font-family="Arial" font-weight="700">{title}</text>

      <text x="72" y="705" fill="#b8ffd4" font-size="18" font-family="Arial" letter-spacing="4">EARTHLENS MOCK SATELLITE LAYER</text>
    </svg>
    """

    svg_bytes = svg.encode("utf-8")
    encoded = base64.b64encode(svg_bytes).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"


def generate_mock_scan(city: str, user_type: str, layer_focus: str) -> ScanResponse:
    green_pct = 42.8
    dense_pct = 18.6
    water_pct = 9.7
    built_up_pct = 31.4
    mean_ndvi = 0.51
    mean_ndwi = 0.18
    mean_ndbi = 0.27
    heat_risk_score = 58.0
    reliability_score = 91.0

    return ScanResponse(
        layers=LayerImages(
            rgb=svg_layer("RGB Natural Color", "rgb"),
            ndvi=svg_layer("NDVI Vegetation Health", "ndvi"),
            ndwi=svg_layer("NDWI Water Signal", "ndwi"),
            ndbi=svg_layer("NDBI Built-Up Surface", "ndbi"),
            savi=svg_layer("SAVI Soil Adjusted Vegetation", "savi"),
            classification=svg_layer("Land Classification", "classification"),
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
        ),
        metadata=ScanMetadata(
            city=city,
            cloud_cover=6.4,
            date="2026-04-28",
            satellite="Sentinel-2 L2A mock mode",
            resolution="10m target resolution",
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