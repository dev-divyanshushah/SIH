"""
Battery Health Model Training
================================
Trains RandomForest Regressor to predict State of Health (%).

Run: python scripts/train_battery_model.py
"""
import os, sys, json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = os.path.join(os.path.dirname(__file__), '..')
DATA_PATH = os.path.join(ROOT, 'data', 'synthetic', 'battery_dataset.csv')
MODEL_DIR = os.path.join(ROOT, 'models', 'battery_model')
REPORT_DIR = os.path.join(ROOT, 'reports')

FEATURES = ["cycle_count", "average_temperature", "depth_of_discharge",
            "current_capacity_ratio", "voltage_sag"]
TARGET = "state_of_health"
RANDOM_SEED = 42


def eval_model(model, X, y, name):
    p = model.predict(X)
    mae = mean_absolute_error(y, p)
    rmse = np.sqrt(mean_squared_error(y, p))
    r2 = r2_score(y, p)
    print(f"  {name:28s} MAE={mae:.3f}  RMSE={rmse:.3f}  R²={r2:.4f}")
    return {"model": name, "MAE": round(mae, 4), "RMSE": round(rmse, 4), "R2": round(r2, 4)}


def main():
    print("=" * 60)
    print("PERSIST-AIR Battery Health Model Training")
    print("Data: SYNTHETIC — not real battery cycle data")
    print("=" * 60)

    if not os.path.exists(DATA_PATH):
        print(f"Dataset not found: {DATA_PATH}")
        print("Run: python scripts/generate_battery_dataset.py")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    print(f"\nLoaded: {df.shape[0]} samples")

    X = df[FEATURES].values
    y = df[TARGET].values

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=RANDOM_SEED)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=RANDOM_SEED)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    print("\n--- Validation Results ---")
    results = []
    models = {}

    lr = LinearRegression()
    lr.fit(X_train_s, y_train)
    models["LinearRegression"] = lr
    results.append(eval_model(lr, X_val_s, y_val, "Linear Regression"))

    rf = RandomForestRegressor(n_estimators=150, max_depth=12,
                                min_samples_leaf=3, random_state=RANDOM_SEED, n_jobs=-1)
    rf.fit(X_train_s, y_train)
    models["RandomForest"] = rf
    results.append(eval_model(rf, X_val_s, y_val, "Random Forest"))

    best_r = min(results, key=lambda r: r["RMSE"])
    best_model = models[best_r["model"].replace(" ", "")]
    print(f"\n✓ Best: {best_r['model']} (RMSE={best_r['RMSE']:.3f})")

    print("\n--- Final Test ---")
    test_r = eval_model(best_model, X_test_s, y_test, best_r["model"] + " (TEST)")
    print("⚠ NOTE: Synthetic/Simulation-based evaluation")

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump({
        "model": best_model,
        "scaler": scaler,
        "features": FEATURES,
        "target": TARGET,
        "metadata": {
            "model_name": "battery_health_v1",
            "algorithm": best_r["model"],
            "training_date": datetime.utcnow().isoformat() + "Z",
            "dataset": "synthetic_battery_v1",
            "n_train": len(X_train),
            "test_metrics": test_r,
            "data_label": "SYNTHETIC/SIMULATION-BASED",
        }
    }, os.path.join(MODEL_DIR, "model.joblib"))

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(os.path.join(REPORT_DIR, "battery_model_report.json"), "w") as f:
        json.dump({"model": "battery_health_v1", "data": "SYNTHETIC",
                   "results": results, "test": test_r,
                   "training_date": datetime.utcnow().isoformat() + "Z"}, f, indent=2)

    print(f"\n✓ Model saved: {MODEL_DIR}/model.joblib")
    print(f"✓ Report saved: {REPORT_DIR}/battery_model_report.json")


if __name__ == "__main__":
    main()
