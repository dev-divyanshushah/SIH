"""
ML Factory
===========
Loads real trained ML models if available; falls back to simulation mocks.
All model_source fields clearly indicate REAL_MODEL vs SIMULATION.

To integrate real models:
1. Run: python scripts/train_energy_model.py (and others)
2. The factory will auto-detect model files in models/ and load them.
"""
import os
import logging

logger = logging.getLogger("persist-air.ml")

# Always available: simulation mocks
from app.ml.mocks import (
    MockObjectDetector, MockBehaviourAnalyser, MockRiskScorer,
    MockEndurancePredictor, MockFeasibilityPredictor, MockBatteryHealthPredictor,
)

# ─── Try loading real trained models ─────────────────────────────────────────

def _try_load_real_energy():
    """Try to load the trained energy endurance model."""
    model_path = os.path.join("models", "energy_model", "model.joblib")
    if not os.path.exists(model_path):
        logger.info("Energy model not found — using SIMULATION mock")
        return MockEndurancePredictor()
    try:
        from app.ml.real_energy import RealEndurancePredictor
        predictor = RealEndurancePredictor(model_path)
        logger.info(f"✓ Real energy model loaded from {model_path}")
        return predictor
    except Exception as e:
        logger.warning(f"Real energy model failed to load ({e}) — using SIMULATION mock")
        return MockEndurancePredictor()


def _try_load_real_anomaly():
    """Try to load the trained anomaly detection model."""
    model_path = os.path.join("models", "anomaly_model", "model.joblib")
    if not os.path.exists(model_path):
        logger.info("Anomaly model not found — using SIMULATION mock")
        return MockBehaviourAnalyser()
    try:
        from app.ml.real_anomaly import RealBehaviourAnalyser
        analyser = RealBehaviourAnalyser(model_path)
        logger.info(f"✓ Real anomaly model loaded from {model_path}")
        return analyser
    except Exception as e:
        logger.warning(f"Real anomaly model failed to load ({e}) — using SIMULATION mock")
        return MockBehaviourAnalyser()


def _try_load_real_battery():
    """Try to load the trained battery health model."""
    model_path = os.path.join("models", "battery_model", "model.joblib")
    if not os.path.exists(model_path):
        logger.info("Battery health model not found — using SIMULATION mock")
        return MockBatteryHealthPredictor()
    try:
        from app.ml.real_battery import RealBatteryHealthPredictor
        predictor = RealBatteryHealthPredictor(model_path)
        logger.info(f"✓ Real battery model loaded from {model_path}")
        return predictor
    except Exception as e:
        logger.warning(f"Real battery model failed to load ({e}) — using SIMULATION mock")
        return MockBatteryHealthPredictor()


# ─── Instantiate all models ───────────────────────────────────────────────────

object_detector       = MockObjectDetector()          # YOLO model lives in ml_service/
behaviour_analyser    = _try_load_real_anomaly()
risk_scorer           = MockRiskScorer()              # rule-based, no training needed
endurance_predictor   = _try_load_real_energy()
feasibility_predictor = MockFeasibilityPredictor()    # deterministic energy budget
battery_health_predictor = _try_load_real_battery()
