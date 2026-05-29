# MudBot Agri-AI

MudBot Agri-AI recommends crops and allocates field zones using real-time soil sensor data: moisture, salinity (dS/m), temperature (°C), and pH. Optimized for Nile Delta farming, it supports three modes: Normal (auto-rank all crops), Enhanced (rank user-selected crops), and Scan (IDW interpolation + zone allocation).

Prerequisites
- Python 3.10+
- pip

Install
```
python -m venv .venv
pip install -r requirements.txt
```

Quick start
From project root:
```
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Run tests
```
pytest tests/
```

API examples
Normal mode:
```
curl -X POST http://localhost:8000/api/normal \
  -H "Content-Type: application/json" \
  -d '{"moisture":0.65,"salinity":1.5,"temperature":28,"ph":6.5}'
```
Enhanced mode:
```
curl -X POST http://localhost:8000/api/enhanced \
  -H "Content-Type: application/json" \
  -d '{"soil":{"moisture":0.65,"salinity":1.5,"temperature":28,"ph":6.5},"crops":["Rice","Wheat"]}'
```
Scan mode:
```
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"readings":[{"moisture":0.65,"salinity":1.5,"temperature":28,"ph":6.5,"lat":31,"lon":31}],"allocations":{"Rice":0.6,"Wheat":0.4}}'
```

Repository: https://github.com/Nadoooor/Terraskipper_ML_Model

License: MIT

## TensorFlow Lite Integration

This project includes an optional TensorFlow training + TFLite export pipeline and a lightweight TFLite runner for on-device inference.

1. Train and export a TFLite model:

```
python models/train_tf.py
```

This will produce:
- models/suitability_model_tf/   (SavedModel)
- models/suitability_model.tflite
- models/scaler_tf.pkl
- models/features_tf.json

2. Run inference with the TFLite scorer (example):

```python
from ai.tflite_runner import TFLiteScorer
from ai.scorer import SoilReading

scorer = TFLiteScorer()
if scorer.is_ready():
    reading = SoilReading(0.65, 1.5, 28, 6.5)
    print(scorer.score_all(reading)[:5])
else:
    print('TFLite model not found or artifacts missing')
```

Notes:
- TensorFlow (>=2.13) is required to run training and to convert to TFLite on most platforms. For lightweight inference on certain platforms, consider installing `tflite-runtime` instead of full TensorFlow.
- The TFLite runner mirrors the scorer API but returns only the model score (no per-parameter breakdown).
