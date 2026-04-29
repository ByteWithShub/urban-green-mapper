def get_layer_explanation(layer_name: str) -> str:
    return {
        "RGB Satellite": "This is the real-color satellite image using red, green, and blue bands.",
        "Vegetation / NDVI": "NDVI highlights vegetation health. Higher values usually mean healthier or denser vegetation.",
        "Water / NDWI": "NDWI highlights water or moisture. Higher values may indicate water bodies, wet soil, or moisture-rich surfaces.",
        "Built-up / NDBI": "NDBI helps identify built-up surfaces such as roads, roofs, concrete, and dense urban areas.",
        "Soil-adjusted vegetation / SAVI": "SAVI highlights vegetation while reducing soil brightness effects.",
        "Land Cover Classes": "This classifies the scene into broad zones: non-green, low vegetation, moderate vegetation, and dense vegetation.",
        "Risk Overlay": "This combines low vegetation and built-up signal to highlight possible heat-vulnerable areas."
    }.get(layer_name, "No explanation available.")


def get_legend(layer_name: str) -> dict:
    return {
        "Vegetation / NDVI": {
            "Low / no vegetation": "NDVI < 0.20",
            "Low vegetation": "0.20 - 0.40",
            "Moderate vegetation": "0.40 - 0.60",
            "Dense vegetation": "0.60+",
        },
        "Water / NDWI": {
            "Low water signal": "NDWI < 0",
            "Possible moisture": "0 - 0.30",
            "Strong water signal": "0.30+",
        },
        "Built-up / NDBI": {
            "Low built-up signal": "NDBI < 0",
            "Mixed surface": "0 - 0.20",
            "Stronger built-up signal": "0.20+",
        },
        "Soil-adjusted vegetation / SAVI": {
            "Low vegetation": "SAVI < 0.20",
            "Moderate vegetation": "0.20 - 0.50",
            "Dense vegetation": "0.50+",
        },
        "Land Cover Classes": {
            "0": "Non-green / built-up / water / bare",
            "1": "Low vegetation",
            "2": "Moderate vegetation",
            "3": "Dense vegetation",
        },
        "Risk Overlay": {
            "0": "Lower risk",
            "1": "Moderate risk",
            "2": "Higher risk",
        }
    }.get(layer_name, {})