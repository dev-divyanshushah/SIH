"""
Energy Endurance Model Training
==================================
Trains and evaluates 3 models on synthetic energy data.
Selects best model by validation RMSE and saves to models/energy_model/.

Models compared:
  1. Linear Regression (baseline)
  2. Random Forest Regressor
  3. XGBoost Regressor (if available)

Metrics: MAE, RMSE, R²
Label: SYNTHETIC/SIMULATION-BASED EVALUATION

Run: python scripts/train_energy_model.py
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = os.path.join(os.path.dirname(__file__), '..')
DATA_PATH = os.path.join(ROOT, 'data', 'synthetic', 'energy_dataset.csv')
MODEL_DIR = os.path.join(ROOT, 'models', 'energy_model')
REPORT_DIR = os.path.join(ROOT, 'reports')

FEATURES = [
    "battery_percentage", "battery_voltage", "current_consumption",
    "temperature", "airspeed", "altitude", "distance_from_base",
    "wind_factor", "payload_weight",
]
TARGET = "remaining_endurance_minutes"
RANDOM_SEED = 42


def evaluate(model, X_test, y_test, name):
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    print(f"  {name:30s} MAE={mae:.3f}  RMSE={rmse:.3f}  R²={r2:.4f}")
    return {"model": name, "MAE": round(mae, 4), "RMSE": round(rmse, 4), "R2": round(r2, 4)}


def main():
    print("=" * 60)
    print("PERSIST-AIR Energy Model Training")
    print("Data: SYNTHETIC (physics-inspired, not real UAV data)")
    print("=" * 60)

    # ── Load data ────────────────────────────────────────────────
    if not os.path.exists(DATA_PATH):
        print(f"Dataset not found: {DATA_PATH}")
        print("Run: python scripts/generate_energy_dataset.py")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    print(f"\nLoaded dataset: {df.shape[0]} samples, {df.shape[1]} columns")

    X = df[FEATURES].values
    y = df[TARGET].values

    # ── Split ────────────────────────────────────────────────────
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=RANDOM_SEED)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=RANDOM_SEED)

    print(f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")

    # ── Scaler ───────────────────────────────────────────────────
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    # ── Train models ─────────────────────────────────────────────
    print("\n--- Validation Results ---")
    results = []
    models = {}

    # 1. Linear Regression
    lr = LinearRegression()
    lr.fit(X_train_s, y_train)
    models["LinearRegression"] = (lr, True)  # True = needs scaling
    results.append(evaluate(lr, X_val_s, y_val, "Linear Regression"))

    # 2. Random Forest (no scaling needed but we use scaled for consistency)
    rf = RandomForestRegressor(n_estimators=150, max_depth=15,
                                min_samples_leaf=3, random_state=RANDOM_SEED, n_jobs=-1)
    rf.fit(X_train_s, y_train)
    models["RandomForest"] = (rf, True)
    results.append(evaluate(rf, X_val_s, y_val, "Random Forest"))

    # 3. XGBoost (optional)
    try:
        from xgboost import XGBRegressor
        xgb = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.05,
                            subsample=0.8, colsample_bytree=0.8,
                            random_state=RANDOM_SEED, verbosity=0)
        xgb.fit(X_train_s, y_train)
        models["XGBoost"] = (xgb, True)
        results.append(evaluate(xgb, X_val_s, y_val, "XGBoost"))
    except ImportError:
        print("  XGBoost not available — skipping")

    # ── Select best model ────────────────────────────────────────
    best = min(results, key=lambda r: r["RMSE"])
    best_model, needs_scale = models[best["model"].replace(" ", "")]
    print(f"\n✓ Best model: {best['model']} (RMSE={best['RMSE']:.3f})")

    # ── Final test evaluation ────────────────────────────────────
    print("\n--- Final Test Evaluation ---")
    test_result = evaluate(best_model, X_test_s, y_test, best["model"] + " (TEST)")
    print(f"\n⚠ NOTE: All metrics based on SYNTHETIC data — not real UAV flights")

    # ── Save ─────────────────────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump({
        "model": best_model,
        "scaler": scaler,
        "features": FEATURES,
        "target": TARGET,
        "metadata": {
            "model_name": f"energy_model_v1",
            "algorithm": best["model"],
            "training_date": datetime.utcnow().isoformat() + "Z",
            "dataset": "synthetic_energy_v1",
            "n_train": len(X_train),
            "training_metrics": best,
            "test_metrics": test_result,
            "data_label": "SYNTHETIC/SIMULATION-BASED — not real UAV flight data",
            "features": FEATURES,
        }
    }, os.path.join(MODEL_DIR, "model.joblib"))

    # Save report
    os.makedirs(REPORT_DIR, exist_ok=True)
    report = {
        "model": "energy_endurance_v1",
        "data": "SYNTHETIC/SIMULATION-BASED",
        "algorithm": best["model"],
        "validation_results": results,
        "test_results": test_result,
        "training_date": datetime.utcnow().isoformat() + "Z",
    }
    with open(os.path.join(REPORT_DIR, "energy_model_report.json"), "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Model saved: {MODEL_DIR}/model.joblib")
    print(f"✓ Report saved: {REPORT_DIR}/energy_model_report.json")
    print("\nTo use the real model, restart the backend.")
    print("factory.py will auto-detect and load it.")


if __name__ == "__main__":
    main()
