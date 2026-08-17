"""
Mock ML Implementations
========================
These implement realistic mock behavior for all 5 ML models.
Each mock uses domain-appropriate logic, not pure random values.

REPLACE THESE with real model inference when your ML models are trained.
See base.py for the interface contracts.
"""

import random
import math
import time
import uuid
from datetime import datetime, timedelta
from app.ml.base import (
    BaseObjectDetector, BaseBehaviourAnalyser, BaseRiskScorer,
    BaseEndurancePredictor, BaseFeasibilityPredictor,
    DetectionInput, DetectionOutput,
    BehaviourInput, BehaviourOutput,
    RiskInput, RiskOutput,
    EnduranceInput, EnduranceOutput,
    FeasibilityInput, FeasibilityOutput,
)

# ─── Mock Object Detector ────────────────────────────────────────────────────
SECURITY_OBJECTS = ["vehicle", "person", "motorcycle", "truck", "group", "abandoned_object"]
HUMANITARIAN_OBJECTS = ["stranded_person", "crowd", "fire", "smoke", "flooded_area", "damaged_structure"]
ENVIRONMENTAL_OBJECTS = ["fire", "deforestation", "pollution", "ecological_anomaly", "water_change"]

class MockObjectDetector(BaseObjectDetector):
    """
    MOCK: Returns simulated detections.
    REPLACE WITH: YOLOv8/RT-DETR model inference against actual video frames.
    """

    async def detect(self, inp: DetectionInput) -> DetectionOutput:
        t0 = time.time()
        mode = inp.operational_mode
        candidates = (SECURITY_OBJECTS if mode == "security"
                       else HUMANITARIAN_OBJECTS if mode == "humanitarian"
                       else ENVIRONMENTAL_OBJECTS)

        num_detections = random.choices([0, 1, 2, 3], weights=[40, 40, 15, 5])[0]
        detections = []
        for _ in range(num_detections):
            obj = random.choice(candidates)
            detections.append({
                "id": uuid.uuid4().hex[:8],
                "class": obj,
                "confidence": round(random.uniform(0.72, 0.98), 3),
                "bbox": [
                    random.randint(100, 400), random.randint(100, 300),
                    random.randint(50, 200), random.randint(50, 150),
                ],
                "risk": "high" if obj in ("vehicle", "fire", "stranded_person") else "medium",
            })

        return DetectionOutput(
            detections=detections,
            frame_id=inp.frame_id,
            processing_time_ms=round((time.time() - t0) * 1000 + random.uniform(20, 80), 2),
        )


# ─── Mock Behaviour Analyser ─────────────────────────────────────────────────
BEHAVIOUR_PATTERNS = {
    "vehicle": [
        ("circling", "Direct transit or parking", "Circular path detected around restricted area", 87),
        ("stationary_extended", "Transit through sector", "Vehicle stationary >14 min in restricted zone", 79),
        ("erratic_movement", "Steady traffic flow", "Sudden speed changes and direction reversals", 68),
    ],
    "person": [
        ("boundary_crossing", "Normal public movement", "Person crossed restricted boundary", 74),
        ("loitering", "Passing through", "Individual stationary >10 min near entry point", 61),
    ],
    "abandoned_object": [
        ("unattended", "Object should be moving with person", "Object stationary for extended period", 72),
    ],
}

class MockBehaviourAnalyser(BaseBehaviourAnalyser):
    """
    MOCK: Simulates temporal behaviour analysis.
    REPLACE WITH: LSTM/Transformer model trained on trajectory data.
    """

    async def analyse(self, inp: BehaviourInput) -> BehaviourOutput:
        patterns = BEHAVIOUR_PATTERNS.get(inp.object_class, [])
        if not patterns or random.random() < 0.25:
            return BehaviourOutput(
                anomaly_detected=False,
                behaviour_type=None,
                anomaly_score=random.uniform(5, 25),
                confidence=random.uniform(0.85, 0.97),
                description="Normal behaviour pattern observed.",
                normal_pattern="Expected movement for this sector.",
                observed_pattern="Movement consistent with expected pattern.",
            )

        btype, normal, observed, base_score = random.choice(patterns)
        score = base_score + random.uniform(-8, 8)
        return BehaviourOutput(
            anomaly_detected=True,
            behaviour_type=btype,
            anomaly_score=round(score, 1),
            confidence=round(random.uniform(0.80, 0.96), 3),
            description=f"Anomalous behaviour: {btype.replace('_', ' ')} detected.",
            normal_pattern=normal,
            observed_pattern=observed,
        )


# ─── Mock Risk Scorer ─────────────────────────────────────────────────────────
class MockRiskScorer(BaseRiskScorer):
    """
    MOCK: Computes risk score from multiple factors.
    REPLACE WITH: Trained classifier or rule-based expert system.
    """

    async def score(self, inp: RiskInput) -> RiskOutput:
        obj_score = {
            "vehicle": 25, "person": 20, "motorcycle": 18, "truck": 28,
            "fire": 30, "abandoned_object": 15, "stranded_person": 22,
            "crowd": 16, "deforestation": 18, "group": 20,
        }.get(inp.object_class, 15)

        restricted_score = 20 if inp.in_restricted_zone else 5
        behaviour_score = int(inp.anomaly_score * 0.25) if inp.behaviour_anomaly else 5
        persistence_score = min(15, int(inp.duration_minutes * 0.5))
        confidence_score = int(inp.confidence * 8)

        total = obj_score + restricted_score + behaviour_score + persistence_score + confidence_score
        total = max(0, min(100, total))

        if total <= 30:
            level = "low"
        elif total <= 60:
            level = "medium"
        elif total <= 80:
            level = "high"
        else:
            level = "critical"

        return RiskOutput(
            risk_score=total,
            risk_level=level,
            breakdown={
                "object_classification": obj_score,
                "restricted_zone": restricted_score,
                "behaviour_anomaly": behaviour_score,
                "persistence": persistence_score,
                "confidence": confidence_score,
            },
            explanation=(
                f"Risk {total}/100 ({level.upper()}). "
                f"Primary factors: object class (+{obj_score}), "
                f"restricted zone (+{restricted_score}), "
                f"behaviour anomaly (+{behaviour_score})."
            ),
        )


# ─── Mock Endurance Predictor ─────────────────────────────────────────────────
class MockEndurancePredictor(BaseEndurancePredictor):
    """
    MOCK: Predicts remaining endurance using physics-based heuristics.
    REPLACE WITH: LSTM model trained on real flight telemetry data.
    """

    async def predict(self, inp: EnduranceInput) -> EnduranceOutput:
        # Base drain: ~1.4% per minute at cruise
        base_drain = 1.4

        # Adjustments
        speed_factor = (inp.airspeed / 14.0) ** 1.5
        altitude_factor = 1.0 + (inp.altitude - 100) / 2000
        temp_factor = 1.0 + max(0, (inp.temperature - 30)) * 0.01
        wind_factor = inp.wind_factor
        payload_factor = 1.0 + inp.payload_weight * 0.02

        effective_drain = base_drain * speed_factor * altitude_factor * temp_factor * wind_factor * payload_factor

        usable_pct = max(0, inp.battery_percentage - 8.0)
        total_remaining = usable_pct / effective_drain

        # Return reserve: time to fly back at max speed
        return_time = (inp.distance_from_base / 1000) / (inp.airspeed * 1.1) * 60  # minutes
        safe_time = max(0, total_remaining - return_time)

        # Risk assessment
        if safe_time > 20:
            risk = "low"
        elif safe_time > 10:
            risk = "medium"
        elif safe_time > 5:
            risk = "high"
        else:
            risk = "critical"

        # Predicted curve (next 40 minutes)
        curve = []
        current_pct = inp.battery_percentage
        for t in range(0, 41, 2):
            curve.append({"t": t, "pct": round(max(0, current_pct - effective_drain * t), 1)})

        return EnduranceOutput(
            remaining_endurance_minutes=round(total_remaining, 1),
            safe_mission_time=round(safe_time, 1),
            return_reserve_minutes=round(return_time, 1),
            energy_risk=risk,
            confidence=round(random.uniform(0.87, 0.96), 3),
            predicted_battery_curve=curve,
        )


# ─── Mock Feasibility Predictor ───────────────────────────────────────────────
class MockFeasibilityPredictor(BaseFeasibilityPredictor):
    """
    MOCK: Determines if a drone can safely complete a mission.
    REPLACE WITH: Multi-factor ML model with real flight data calibration.
    """

    async def predict(self, inp: FeasibilityInput) -> FeasibilityOutput:
        # Energy %/km at cruise (rough)
        energy_per_km = 2.8
        to_target_km = inp.distance_to_target_m / 1000
        return_km = inp.return_distance_m / 1000

        mission_energy = (to_target_km + return_km) * energy_per_km + inp.estimated_investigation_minutes * 1.4
        return_reserve = 8.0  # always keep 8%
        required_total = mission_energy + return_reserve
        usable = max(0, inp.battery_percentage - return_reserve)

        if usable >= mission_energy + 5:
            result = "FEASIBLE"
        elif usable >= mission_energy:
            result = "MARGINAL"
        else:
            result = "NOT_FEASIBLE"

        eta = datetime.utcnow() + timedelta(minutes=inp.estimated_investigation_minutes + to_target_km * 4)

        # Recommendation
        if result == "NOT_FEASIBLE":
            rec = "Assign a drone with higher battery level. This drone has insufficient endurance to complete the mission safely."
        elif result == "MARGINAL":
            rec = "Mission possible but energy margins are tight. Consider reducing investigation time or assigning a drone with more battery."
        else:
            rec = "Drone has sufficient energy to complete the mission with safe return reserve."

        return FeasibilityOutput(
            result=result,
            estimated_mission_energy=round(mission_energy, 1),
            available_usable_energy=round(usable, 1),
            required_return_reserve=return_reserve,
            predicted_completion_time=eta.strftime("%H:%M:%S"),
            confidence=round(random.uniform(0.88, 0.96), 3),
            recommendation=rec,
        )
