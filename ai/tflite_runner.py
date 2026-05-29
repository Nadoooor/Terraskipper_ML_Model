import os
import json
import joblib
import numpy as np
import pandas as pd

# Try to import TensorFlow or fallback to tflite_runtime
try:
    import tensorflow as tf
    _TFLITE_INTERPRETER = tf.lite.Interpreter
except Exception:
    try:
        from tflite_runtime.interpreter import Interpreter as _TFLITE_INTERPRETER
        tf = None
    except Exception:
        _TFLITE_INTERPRETER = None


class TFLiteScorer:
    """Lightweight TFLite scorer that mirrors CropScorer.score_all output.

    Expects the following artifacts (created by models/train_tf.py):
      - models/suitability_model.tflite
      - models/scaler_tf.pkl
      - models/features_tf.json
    """

    def __init__(self, tflite_path='models/suitability_model.tflite',
                 scaler_path='models/scaler_tf.pkl',
                 features_path='models/features_tf.json',
                 crop_db_path='config/crop_database.csv'):
        self.tflite_path = tflite_path
        self.scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None
        self.features = json.load(open(features_path)) if os.path.exists(features_path) else None
        self.crops_df = pd.read_csv(crop_db_path)
        self.interpreter = None

        if _TFLITE_INTERPRETER is not None and os.path.exists(self.tflite_path):
            try:
                self.interpreter = _TFLITE_INTERPRETER(model_path=self.tflite_path)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
            except Exception as e:
                print("[TFLITE] Interpreter failed to load:", e)
                self.interpreter = None

    def is_ready(self) -> bool:
        return self.interpreter is not None and self.scaler is not None and self.features is not None

    def _make_feature_vector(self, crop_name, reading):
        # features is a list of column names used during training (order matters)
        feat = {k: 0.0 for k in self.features}
        feat['moisture'] = float(reading.moisture)
        feat['salinity'] = float(reading.salinity)
        feat['temperature'] = float(reading.temperature)
        feat['ph'] = float(reading.ph)
        crop_col = f"crop_{crop_name}"
        if crop_col in feat:
            feat[crop_col] = 1.0
        X = np.array([feat[c] for c in self.features], dtype=np.float32).reshape(1, -1)
        if self.scaler is not None:
            X = self.scaler.transform(X)
        return X

    def score_all(self, reading):
        """Return a list of {crop, score, breakdown, notes} sorted by score desc."""
        results = []
        for crop in self.crops_df['crop']:
            X = self._make_feature_vector(crop, reading)
            try:
                self.interpreter.set_tensor(self.input_details[0]['index'], X.astype(np.float32))
                self.interpreter.invoke()
                out = self.interpreter.get_tensor(self.output_details[0]['index'])
                score = float(out.flatten()[0])
            except Exception as e:
                # On failure, give a zero score but continue
                score = 0.0
            results.append({
                'crop': crop,
                'score': round(score, 1),
                'breakdown': {},
                'notes': ''
            })
        return sorted(results, key=lambda x: x['score'], reverse=True)
