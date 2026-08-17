"""
ML Factory
===========
Swap mock implementations for real ones by changing these imports.
"""
from app.ml.mocks import (
    MockObjectDetector, MockBehaviourAnalyser, MockRiskScorer,
    MockEndurancePredictor, MockFeasibilityPredictor,
)

# ─── To integrate real models, replace these instantiations ──────────────────
# from app.ml.real_detector import RealObjectDetector
# object_detector = RealObjectDetector(model_path="models/yolov8.pt")

object_detector = MockObjectDetector()
behaviour_analyser = MockBehaviourAnalyser()
risk_scorer = MockRiskScorer()
endurance_predictor = MockEndurancePredictor()
feasibility_predictor = MockFeasibilityPredictor()
