# MudBot Agri-AI: Precision Agriculture System for Nile Delta Farming

## Overview

MudBot Agri-AI is an intelligent crop recommendation and land allocation system designed for the Nile Delta region. It leverages real-time soil sensor data (moisture, salinity, temperature, pH) to:

1. **Recommend suitable crops** based on current soil conditions
2. **Optimize crop selection** from a user-provided shortlist
3. **Allocate agricultural zones** across a scanned area for maximum productivity

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run the API Server

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests

```bash
pytest tests/
```

## System Architecture

### Three Operating Modes

#### Mode 1: Normal Mode (`/api/normal`)
- Auto-ranks **ALL 20 crops** in the database
- Returns top 5 recommendations with full parameter breakdown
- Use case: General suitability assessment at any point

#### Mode 2: Enhanced Mode (`/api/enhanced`)
- Ranks only a **user-supplied crop list**
- Returns ranked recommendations for those specific crops
- Use case: When you've pre-selected candidate crops

#### Mode 3: Scan Mode (`/api/scan`)
- Processes **multiple GPS-tagged readings** across a field
- Interpolates suitability surfaces via IDW (Inverse Distance Weighting)
- Performs **greedy zone allocation** to assign land parcels to crops
- Generates interactive Folium maps for visualization
- Use case: Full-field planning and zone demarcation

## Project Structure

```
mudbot_agri_ai/
├── config/
│   ├── crop_database.csv          # Master crop dataset
│   └── settings.yaml              # Thresholds, weights, API keys
├── data/
│   ├── raw/                       # Raw sensor readings (JSON)
│   ├── processed/                 # Cleaned feature vectors
│   └── scans/                     # GPS + reading archives per session
├── models/
│   ├── train_model.py             # Training pipeline
│   ├── suitability_model.pkl      # Serialized Random Forest
│   └── scaler.pkl                 # Saved StandardScaler
├── ai/
│   ├── scorer.py                  # Core suitability scoring engine
│   ├── normal_mode.py             # Mode 1 logic
│   ├── enhanced_mode.py           # Mode 2 logic
│   ├── scan_mode.py               # Mode 3 logic + zone optimizer
│   └── explainability.py          # SHAP wrapper for explainable AI
├── sensors/
│   ├── gps_reader.py              # GPS NMEA parsing
│   ├── moisture_reader.py         # ADC/I2C moisture interface
│   ├── salinity_reader.py         # EC sensor interface
│   └── temp_reader.py             # DS18B20 or thermistor
├── mapping/
│   ├── heatmap.py                 # Folium heatmap generator
│   ├── zone_map.py                # Zone allocation visualizer
│   └── interpolation.py           # IDW spatial interpolation
├── api/
│   ├── main.py                    # FastAPI application
│   ├── routes/
│   │   ├── normal.py
│   │   ├── enhanced.py
│   │   └── scan.py
│   └── schemas.py                 # Pydantic request/response models
├── tests/
│   ├── test_scorer.py
│   ├── test_scan_mode.py
│   └── test_api.py
├── notebooks/
│   ├── EDA_crop_dataset.ipynb
│   ├── model_training.ipynb
│   └── scan_mode_demo.ipynb
├── requirements.txt
└── README.md
```

## API Reference

### Normal Mode: `/api/normal`

**Request:**
```json
{
  "moisture": 0.65,
  "salinity": 1.5,
  "temperature": 28,
  "ph": 6.5,
  "lat": 31.0,
  "lon": 31.0
}
```

**Response:**
```json
{
  "mode": "normal",
  "location": {"lat": 31.0, "lon": 31.0},
  "soil_input": {...},
  "recommendations": [
    {
      "crop": "Rice",
      "score": 92.3,
      "breakdown": {...},
      "notes": "Requires flooded or saturated soil"
    }
  ]
}
```

### Enhanced Mode: `/api/enhanced`

**Request:**
```json
{
  "soil": {
    "moisture": 0.65,
    "salinity": 1.5,
    "temperature": 28,
    "ph": 6.5
  },
  "crops": ["Rice", "Wheat", "Barley"]
}
```

### Scan Mode: `/api/scan`

**Request:**
```json
{
  "readings": [
    {"moisture": 0.65, "salinity": 1.5, "temperature": 28, "ph": 6.5, "lat": 31.0, "lon": 31.0},
    {"moisture": 0.55, "salinity": 2.0, "temperature": 26, "ph": 6.3, "lat": 31.001, "lon": 31.001}
  ],
  "allocations": {"Rice": 0.60, "Watermelon": 0.40}
}
```

## Crop Database

The system manages **20 crops** optimized for Nile Delta farming with parameters for:
- Moisture range (volumetric water content)
- Salinity tolerance (dS/m)
- Temperature range (°C)
- pH range
- Soil type preferences
- Water requirements
- Weighted parameter importance

See `config/crop_database.csv` for complete crop parameters.

## Model Training

Generate synthetic training data and train the Random Forest model:

```bash
python models/train_model.py
```

This produces:
- `models/suitability_model.pkl` — Trained Random Forest
- `models/scaler.pkl` — Feature scaler
- SHAP explainability plots

## Configuration

### `config/settings.yaml`

```yaml
thresholds:
  min_suitability_score: 50.0
  max_cells_per_zone: 5000

weights:
  default_moisture: 0.30
  default_salinity: 0.25
  default_temperature: 0.30
  default_ph: 0.15

api:
  host: 0.0.0.0
  port: 8000
  debug: false

ml_model:
  n_estimators: 300
  max_depth: 12
  min_samples_leaf: 4
```

## Performance Notes

- **Normal Mode:** <50ms per location (all 20 crops)
- **Enhanced Mode:** <20ms per location (user-selected crops)
- **Scan Mode:** ~2-5s for 100 grid points with 10+ readings

## Nile Delta Agricultural Context

MudBot Agri-AI is optimized for:
- **High salinity tolerance:** Prioritizes crops suited to saline irrigation water (e.g., Cotton, Barley)
- **Seasonal awareness:** Distinguishes winter (Wheat, Barley) vs. summer (Rice, Cotton) crops
- **Water efficiency:** Accounts for irrigation availability
- **Soil types:** Recommends crops matched to clay, loam, and sandy-loam soils

## Future Enhancements

- [ ] Real-time sensor integration with robot telemetry
- [ ] Deep learning for non-linear crop-soil interactions
- [ ] Multi-season crop rotation optimization
- [ ] Weather forecasting integration
- [ ] Mobile app for farmer feedback loops
- [ ] Drone-based thermal imaging for stress detection

## License

MIT License

## Authors

Agricultural AI Team at HackClub
