"""
Real Energy Endurance Predictor
================================
Uses a trained RandomForest/XGBoost model from models/energy_model/.
Falls back to simulation if model unavailable.

Training: python scripts/train_energy_model.py
Data: Synthetic physics-inspired dataset (data/synthetic/energy_dataset.csv)
Label: SYNTHETIC/SIMULATION-BASED — not real UAV flight data
"""
import joblib
import numpy as np
import random
from datetime import datetime
from typing import List, Dict

from app.ml.base import (
    BaseEndurancePredictor, EnduranceInput, EnduranceOutput,
)


FEATURE_NAMES = [
    "battery_percentage", "battery_voltage", "current_consumption",
    "temperature", "airspeed", "altitude", "distance_from_base",
    "wind_factor", "payload_weight",
]


class RealEndurancePredictor(BaseEndurancePredictor):
    """
    Real trained energy endurance predictor.
    Model: RandomForest Regressor trained on synthetic physics-based data.
    Note: Trained on SYNTHETIC data. Label all outputs as SYNTHETIC-BASED.
    """

    def __init__(self, model_path: str):
        data = joblib.load(model_path)
        self.model = data["model"]
        self.scaler = data.get("scaler")
        self.metadata = data.get("metadata", {})
        self.feature_names = data.get("features", FEATURE_NAMES)

    def _make_features(self, inp: EnduranceInput) -> np.ndarray:
        features = [
            inp.battery_percentage,
            inp.battery_voltage,
            inp.current_consumption,
            inp.temperature,
            inp.airspeed,
            inp.altitude,
            inp.distance_from_base,
            inp.wind_factor,
            inp.payload_weight,
        ]
        arr = np.array([features])
        if self.scaler is not None:
            arr = self.scaler.transform(arr)
        return arr

    async def predict(self, inp: EnduranceInput) -> EnduranceOutput:
        X = self._make_features(inp)
        remaining_endurance = float(self.model.predict(X)[0])
        remaining_endurance = max(0.0, remaining_endurance)

        # Return reserve calculation (physics-based, not model-predicted)
        return_time = (inp.distance_from_base / 1000) / max(1, inp.airspeed * 1.1) * 60
        safe_time = max(0.0, remaining_endurance - return_time)

        if safe_time > 20:
            risk = "low"
        elif safe_time > 10:
            risk = "medium"
        elif safe_time > 5:
            risk = "high"
        else:
            risk = "critical"

        # Confidence based on battery level (model more reliable in mid-range)
        conf = 0.93 - abs(inp.battery_percentage - 50) * 0.002
        conf = round(max(0.80, min(0.97, conf)), 3)

        # Predicted battery curve
        drain_per_min = (100 - inp.battery_percentage) / max(1, remaining_endurance + 1) if remaining_endurance > 0 else 1.5
        curve = [
            {"t": t, "pct": round(max(0, inp.battery_percentage - drain_per_min * t), 1)}
            for t in range(0, 41, 2)
        ]

        return EnduranceOutput(
            remaining_endurance_minutes=round(remaining_endurance, 1),
            safe_mission_time=round(safe_time, 1),
            return_reserve_minutes=round(return_time, 1),
            energy_risk=risk,
            confidence=conf,
            predicted_battery_curve=curve,
            model_source="REAL_MODEL (Synthetic Training Data)",
        )
