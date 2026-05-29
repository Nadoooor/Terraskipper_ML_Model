import json
import joblib
import numpy as np
import pandas as pd

import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def generate_synthetic_training_data(crop_db_path: str, n_samples: int = 5000) -> pd.DataFrame:
    """Generate synthetic training data by sampling soil conditions
    and computing ground-truth suitability scores from the physics model.
    """
    from ai.scorer import CropScorer, SoilReading

    crops = pd.read_csv(crop_db_path)
    records = []
    rng = np.random.default_rng(42)

    scorer = CropScorer(crop_db_path)

    for _, crop in crops.iterrows():
        for _ in range(n_samples // len(crops)):
            moisture = rng.uniform(0.20, 1.00)
            salinity = rng.uniform(0.0, 10.0)
            temperature = rng.uniform(10.0, 42.0)
            ph = rng.uniform(4.5, 9.0)

            reading = SoilReading(moisture, salinity, temperature, ph)
            score = scorer.score_crop(crop, reading)

            records.append({
                'crop': crop['crop'],
                'moisture': moisture,
                'salinity': salinity,
                'temperature': temperature,
                'ph': ph,
                'score': score
            })

    return pd.DataFrame(records)


def train_tf(crop_db_path: str, model_dir: str = 'models/suitability_model_tf',
             tflite_out: str = 'models/suitability_model.tflite',
             epochs: int = 12, batch_size: int = 256):
    df = generate_synthetic_training_data(crop_db_path)

    df_enc = pd.get_dummies(df, columns=['crop'])
    feature_cols = [c for c in df_enc.columns if c != 'score']

    X = df_enc[feature_cols].values
    y = df_enc['score'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(X_train.shape[1],)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='linear'),
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=epochs, batch_size=batch_size)

    y_pred = model.predict(X_test)
    print(f"R² = {r2_score(y_test, y_pred):.4f}")
    print(f"RMSE = {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")

    # Persist artifacts
    joblib.dump(scaler, 'models/scaler_tf.pkl')
    with open('models/features_tf.json', 'w') as f:
        json.dump(feature_cols, f)

    # Save SavedModel
    model.save(model_dir)

    # Convert to TFLite
    converter = tf.lite.TFLiteConverter.from_saved_model(model_dir)
    tflite_model = converter.convert()
    with open(tflite_out, 'wb') as f:
        f.write(tflite_model)

    print(f"Saved TFLite model to {tflite_out}")


if __name__ == '__main__':
    train_tf('config/crop_database.csv')
