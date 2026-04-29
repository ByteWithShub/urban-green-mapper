import numpy as np


def safe_index(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    return np.where(denominator == 0, np.nan, numerator / denominator)


def ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    return safe_index(nir - red, nir + red)


def ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
    return safe_index(green - nir, green + nir)


def ndbi(swir: np.ndarray, nir: np.ndarray) -> np.ndarray:
    return safe_index(swir - nir, swir + nir)


def savi(nir: np.ndarray, red: np.ndarray, l: float = 0.5) -> np.ndarray:
    return ((nir - red) / (nir + red + l)) * (1 + l)


def classify_ndvi(ndvi_array: np.ndarray) -> np.ndarray:
    classes = np.zeros_like(ndvi_array, dtype="uint8")
    classes[(ndvi_array >= 0.20) & (ndvi_array < 0.40)] = 1
    classes[(ndvi_array >= 0.40) & (ndvi_array < 0.60)] = 2
    classes[ndvi_array >= 0.60] = 3
    return classes