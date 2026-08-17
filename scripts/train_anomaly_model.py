"""
Anomaly Detection Model Training
====================================
Trains Isolation Forest (unsupervised) on normal behaviour data.
Also trains RandomForest classifier for supervised comparison.

Isolation Forest is the primary model — it doesn't require labeled anomaly data.
It learns the "normal" baseline and flags statistical outliers.

Metrics:
- Isolation Forest: F1, Precision, Recall, ROC-AUC (using labeled test set)
- RandomForest: same metrics for comparison

Run: python scripts/train_anomaly_model.py
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, f1_score, precision_score, recall_score
)

ROOT = os.path.join(os.path.dirname(__file__), '..')
DATA_PATH = os.path.join(ROOT, 'data', 'synthetic', 'anomaly_dataset.csv')
MODEL_DIR = os.path.join(ROOT, 'models', 'anomaly_model')
REPORT_DIR = os.path.join(ROOT, 'reports')

FEATURES = [
    "duration_minutes", "group_size", "time_of_day", "day_of_week",
    "in_restricted_zone", "speed_variance", "direction_changes",
    "distance_from_normal_area",
]
RANDOM_SEED = 42


def main():
    print("=" * 60)
    print("PERSIST-AIR Anomaly Detection Model Training")
    print("Method: Isolation Forest (unsupervised) + RF comparison")
    print("Data: SYNTHETIC — not real surveillance data")
    print("=" * 60)

    if not os.path.exists(DATA_PATH):
        print(f"Dataset not found: {DATA_PATH}")
        print("Run: python scripts/generate_anomaly_dataset.py")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    print(f"\nLoaded: {df.shape[0]} samples | Anomaly rate: {df['is_anomaly'].mean():.1%}")

    X = df[FEATURES].values
    y = df["is_anomaly"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # ── Train Isolation Forest on NORMAL samples only ─────────────
    print("\n--- Training Isolation Forest (unsupervised) ---")
    X_normal = X_train_s[y_train == 0]
    contamination = y_train.mean()   # use known rate from dataset

    iso = IsolationForest(
        n_estimators=200,
        contamination=float(contamination),
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    iso.fit(X_normal)

    # Evaluate on test set (IF predicts -1 for anomalies, 1 for normal)
    iso_preds_raw = iso.predict(X_test_s)
    iso_preds = (iso_preds_raw == -1).astype(int)  # convert to 0/1

    iso_scores = iso.decision_function(X_test_s)  # higher = more normal
    iso_auc = roc_auc_score(y_test, -iso_scores)   # negate: more anomalous = higher score

    print(f"Isolation Forest — Test Results:")
    print(f"  F1:      {f1_score(y_test, iso_preds):.4f}")
    print(f"  Prec:    {precision_score(y_test, iso_preds, zero_division=0):.4f}")
    print(f"  Recall:  {recall_score(y_test, iso_preds, zero_division=0):.4f}")
    print(f"  ROC-AUC: {iso_auc:.4f}")

    # ── Train RandomForest (supervised, for comparison) ───────────
    print("\n--- Training Random Forest (supervised, comparison) ---")
    rf = RandomForestClassifier(n_estimators=150, max_depth=12,
                                 random_state=RANDOM_SEED, n_jobs=-1)
    rf.fit(X_train_s, y_train)
    rf_preds = rf.predict(X_test_s)
    rf_probs = rf.predict_proba(X_test_s)[:, 1]
    rf_auc = roc_auc_score(y_test, rf_probs)

    print(f"Random Forest — Test Results:")
    print(f"  F1:      {f1_score(y_test, rf_preds):.4f}")
    print(f"  Prec:    {precision_score(y_test, rf_preds):.4f}")
    print(f"  Recall:  {recall_score(y_test, rf_preds):.4f}")
    print(f"  ROC-AUC: {rf_auc:.4f}")

    print("\n⚠ NOTE: All metrics based on SYNTHETIC data")
    print("  Isolation Forest is the primary model (no labeled anomalies required)")

    # ── Determine best threshold for IF ──────────────────────────
    # The threshold is the contamination level's decision boundary
    threshold = np.percentile(iso.decision_function(X_train_s), contamination * 100)
    print(f"\nIsolation Forest threshold: {threshold:.4f}")

    # ── Save primary model (Isolation Forest) ─────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump({
        "model": iso,
        "scaler": scaler,
        "features": FEATURES,
        "threshold": threshold,
        "metadata": {
            "model_name": "anomaly_model_v1",
            "algorithm": "IsolationForest",
            "training_date": datetime.utcnow().isoformat() + "Z",
            "dataset": "synthetic_anomaly_v1",
            "n_train": len(X_train),
            "contamination": contamination,
            "test_metrics": {
                "f1": round(f1_score(y_test, iso_preds), 4),
                "precision": round(precision_score(y_test, iso_preds, zero_division=0), 4),
                "recall": round(recall_score(y_test, iso_preds, zero_division=0), 4),
                "roc_auc": round(iso_auc, 4),
            },
            "data_label": "SYNTHETIC/SIMULATION-BASED — not real surveillance data",
        }
    }, os.path.join(MODEL_DIR, "model.joblib"))

    # Save full report
    os.makedirs(REPORT_DIR, exist_ok=True)
    report = {
        "model": "anomaly_detection_v1",
        "data": "SYNTHETIC/SIMULATION-BASED",
        "primary_algorithm": "IsolationForest (unsupervised)",
        "comparison_algorithm": "RandomForest (supervised)",
        "isolation_forest_results": {
            "f1": round(f1_score(y_test, iso_preds), 4),
            "precision": round(precision_score(y_test, iso_preds, zero_division=0), 4),
            "recall": round(recall_score(y_test, iso_preds, zero_division=0), 4),
            "roc_auc": round(iso_auc, 4),
        },
        "random_forest_results": {
            "f1": round(f1_score(y_test, rf_preds), 4),
            "precision": round(precision_score(y_test, rf_preds), 4),
            "recall": round(recall_score(y_test, rf_preds), 4),
            "roc_auc": round(rf_auc, 4),
        },
        "false_positive_rate": {
            "isolation_forest": round(
                confusion_matrix(y_test, iso_preds)[0][1] / max(1, sum(y_test == 0)), 4
            ),
        },
        "training_date": datetime.utcnow().isoformat() + "Z",
    }
    with open(os.path.join(REPORT_DIR, "anomaly_model_report.json"), "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Model saved: {MODEL_DIR}/model.joblib")
    print(f"✓ Report saved: {REPORT_DIR}/anomaly_model_report.json")


if __name__ == "__main__":
    main()
