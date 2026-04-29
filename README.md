# EarthLens: An Urban Green Space Intelligence System

EarthLens is a geospatial intelligence platform that transforms Sentinel-2 satellite imagery into structured environmental insights. It combines satellite data processing, environmental index computation, and multi-level interpretability to analyze urban green space, water distribution, and built environments.

The system goes beyond visualization by generating analytical metrics and audience-aware insights that make satellite data accessible for both general users and research-oriented evaluation.

[ LIVE APPLICATION ] https://urban-green-mapper.vercel.app

---

## Project Overview

This system combines:

* Geospatial Processing for multi-band satellite imagery handling
* Environmental Modeling using vegetation, water, and urban indices
* Analytical Computation for urban metrics and risk estimation
* Structured Insight Generation for different audience levels
* Visualization Pipeline for high-resolution environmental maps

---

## Key Features

* Real-time Sentinel-2 satellite scene retrieval
* NDVI, NDWI, NDBI, and SAVI index computation
* High-resolution map rendering (RGB and derived layers)
* Urban metrics:

  * Vegetation coverage
  * Dense vegetation ratio
  * Built-up intensity
  * Water presence
  * Heat risk score
* Multi-layer visualization:

  * RGB
  * NDVI
  * NDWI
  * NDBI
  * SAVI
  * Classification
  * Heat mapping
* Audience-based insight generation:

  * General interpretation
  * Structured summaries
  * Research-level observations
* Integrated weather context via Open-Meteo

---

## System Flow

EarthLens processes data through the following pipeline:

1. Satellite scene retrieval from Microsoft Planetary Computer
2. Multi-band raster loading using rasterio
3. Index computation using NumPy
4. Metric extraction and environmental scoring
5. Visualization generation using matplotlib
6. Insight generation based on computed results
7. Response delivery to frontend as structured outputs

---

## Technology Stack

Frontend:

* React (Vite)
* Framer Motion

Backend:

* FastAPI
* Gunicorn + Uvicorn
* Rasterio
* NumPy, Pandas
* Matplotlib

Data Sources:

* Sentinel-2 (Microsoft Planetary Computer)
* Open-Meteo API

---

## Project Structure

```txt
urban-green-mapper/

├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── core/
│   │   ├── schemas/
│   │   └── main.py
│   └── requirements.txt

├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api.js
│   │   └── App.jsx
│   └── package.json

└── README.md
```

---

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Notes

* Initial scan latency may be higher due to satellite retrieval and processing
* Free-tier backend may enter sleep mode after inactivity
* Visualization is rendered server-side for consistency and quality

---

## Design Philosophy

The system is designed to make satellite data:

* Interpretable
* Comparable
* Actionable

Rather than presenting raw imagery, EarthLens structures environmental information into measurable and explainable outputs.

---

## Author

Shubhangi Singh || AI Engineer
