import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib


def generate_synthetic_training_data(crop_db_path: str,
                                     n_samples: int = 5000) -> pd.DataFrame:
    """Generate synthetic training data from physics model."""
    from ai.scorer import CropScorer, SoilReading
    
    crops = pd.read_csv(crop_db_path)
    records = []
    rng = np.random.default_rng(42)

    for _, crop in crops.iterrows():
        for _ in range(n_samples // len(crops)):
            moisture    = rng.uniform(0.20, 1.00)
            salinity    = rng.uniform(0.0, 10.0)
            temperature = rng.uniform(10.0, 42.0)
            ph          = rng.uniform(4.5, 9.0)

            scorer  = CropScorer(crop_db_path)
            reading = SoilReading(moisture, salinity, temperature, ph)
            score   = scorer.score_crop(crop, reading)

            records.append({
                'crop':        crop['crop'],
                'moisture':    moisture,
                'salinity':    salinity,
                'temperature': temperature,
                'ph':          ph,
                'score':       score
            })

    return pd.DataFrame(records)


def train(crop_db_path: str, model_out: str = 'models/suitability_model.pkl'):
    """Train Random Forest model."""
    df = generate_synthetic_training_data(crop_db_path)

    df_enc = pd.get_dummies(df, columns=['crop'])
    feature_cols = [c for c in df_enc.columns if c != 'score']

    X = df_enc[feature_cols].values
    y = df_enc['score'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=4,
        n_jobs=-1,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"R² = {r2_score(y_test, y_pred):.4f}")
    print(f"RMSE = {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")

    joblib.dump({'model': model, 'scaler': scaler,
                 'features': feature_cols}, model_out)
    print(f"Model saved → {model_out}")


if __name__ == "__main__":
    train("config/crop_database.csv")
