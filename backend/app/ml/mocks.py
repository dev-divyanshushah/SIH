"""
Mock ML Implementations
========================
Domain-aware simulation implementations for all 6 ML models.
These use realistic physics/domain logic, not random numbers.

CLEARLY LABELLED: model_source = "SIMULATION"

REPLACE WITH real models by updating factory.py.
"""
import random
import math
import time
import uuid
from datetime import datetime, timedelta
from app.ml.base import (
    BaseObjectDetector, BaseBehaviourAnalyser, BaseRiskScorer,
    BaseEndurancePredictor, BaseFeasibilityPredictor, BaseBatteryHealthPredictor,
    DetectionInput, DetectionOutput,
    BehaviourInput, BehaviourOutput,
    RiskInput, RiskOutput,
    EnduranceInput, EnduranceOutput,
    FeasibilityInput, FeasibilityOutput,
    BatteryHealthInput, BatteryHealthOutput,
)

# ─── Object categories by mode ───────────────────────────────────────────────
SECURITY_OBJECTS = ["vehicle", "person", "motorcycle", "truck", "group", "abandoned_object"]
HUMANITARIAN_OBJECTS = ["stranded_person", "crowd", "fire", "smoke", "flooded_area", "damaged_structure"]
ENVIRONMENTAL_OBJECTS = ["fire", "deforestation", "pollution", "ecological_anomaly", "water_change"]


class MockObjectDetector(BaseObjectDetector):
    """
    SIMULATION: Returns domain-appropriate detections.
    REPLACE WITH: YOLOv8n inference on actual video frames (ml_service/object_detection/).
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
                "track_id": random.randint(1000, 9999),
                "risk": "high" if obj in ("vehicle", "fire", "stranded_person") else "medium",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })

        return DetectionOutput(
            detections=detections,
            frame_id=inp.frame_id,
            processing_time_ms=round((time.time() - t0) * 1000 + random.uniform(20, 80), 2),
            model_source="SIMULATION",
        )


# ─── Behaviour Analyser ───────────────────────────────────────────────────────
BEHAVIOUR_PATTERNS = {
    "vehicle": [
        ("circling", "Direct transit or parking",
         "Circular path detected around restricted area", 87,
         "TEMPORAL_SPATIAL_ANOMALY",
         ["activity deviates from normal transit pattern",
          "circular movement near restricted zone",
          "duration exceeds expected transit time"]),
        ("stationary_extended", "Transit through sector",
         "Vehicle stationary >14 min in restricted zone", 79,
         "PERSISTENCE_ANOMALY",
         ["vehicle stationary beyond baseline duration",
          "location within restricted boundary"]),
    ],
    "person": [
        ("boundary_crossing", "Normal public movement",
         "Person crossed restricted boundary", 74,
         "ZONE_VIOLATION",
         ["subject crossed into restricted zone",
          "no authorized access expected at this time"]),
        ("loitering", "Passing through",
         "Individual stationary >10 min near entry point", 61,
         "PERSISTENCE_ANOMALY",
         ["extended stationary period near access point",
          "behaviour inconsistent with transit patterns"]),
    ],
    "abandoned_object": [
        ("unattended", "Object should be moving with person",
         "Object stationary for extended period", 72,
         "UNATTENDED_OBJECT",
         ["object remained stationary after person departed",
          "duration exceeds acceptable threshold"]),
    ],
    "stranded_person": [
        ("distress", "Person should be mobile",
         "Person stationary in hazard zone", 85,
         "HUMANITARIAN_DISTRESS",
         ["individual stationary in flood/hazard zone",
          "extended duration suggests distress"]),
    ],
    "fire": [
        ("spreading", "No fire expected",
         "Active fire spreading laterally", 92,
         "ENVIRONMENTAL_EMERGENCY",
         ["thermal signature confirms active combustion",
          "spread vector detected", "wind-assisted propagation"]),
    ],
}


class MockBehaviourAnalyser(BaseBehaviourAnalyser):
    """
    SIMULATION: Temporal behaviour analysis using rule-based heuristics.
    REPLACE WITH: Isolation Forest trained on real trajectory data (ml_service/).
    """

    async def analyse(self, inp: BehaviourInput) -> BehaviourOutput:
        patterns = BEHAVIOUR_PATTERNS.get(inp.object_class, [])

        # Time-of-day factor: activity at unusual hours is more anomalous
        time_penalty = 15 if (inp.time_of_day < 6 or inp.time_of_day > 22) else 0
        zone_penalty = 20 if inp.in_restricted_zone else 0

        if not patterns or random.random() < 0.25:
            return BehaviourOutput(
                anomaly_detected=False,
                behaviour_type=None,
                anomaly_score=random.uniform(5, 25) + time_penalty * 0.3,
                anomaly_probability=random.uniform(0.05, 0.25),
                confidence=random.uniform(0.85, 0.97),
                anomaly_type="NONE",
                description="Normal behaviour pattern observed.",
                normal_pattern="Expected movement for this sector and time of day.",
                observed_pattern="Movement consistent with expected pattern.",
                reasons=["no significant deviation from baseline"],
                model_source="SIMULATION",
            )

        btype, normal, observed, base_score, atype, reasons = random.choice(patterns)
        score = base_score + time_penalty + zone_penalty + random.uniform(-8, 8)
        score = max(0, min(100, score))
        prob = min(0.99, score / 100 + random.uniform(-0.05, 0.05))

        full_reasons = list(reasons)
        if time_penalty > 0:
            full_reasons.append("activity outside normal time window")
        if zone_penalty > 0:
            full_reasons.append("activity detected in restricted zone")

        return BehaviourOutput(
            anomaly_detected=True,
            behaviour_type=btype,
            anomaly_score=round(score, 1),
            anomaly_probability=round(prob, 3),
            confidence=round(random.uniform(0.80, 0.96), 3),
            anomaly_type=atype,
            description=f"Unusual activity detected: {btype.replace('_', ' ')}. Human verification recommended.",
            normal_pattern=normal,
            observed_pattern=observed,
            reasons=full_reasons,
            model_source="SIMULATION",
        )


# ─── Risk Scorer ─────────────────────────────────────────────────────────────
class MockRiskScorer(BaseRiskScorer):
    """
    SIMULATION: Multi-factor weighted risk scoring.
    REPLACE WITH: Calibrated scoring model with operational domain weights.
    """

    async def score(self, inp: RiskInput) -> RiskOutput:
        obj_score = {
            "vehicle": 25, "person": 20, "motorcycle": 18, "truck": 28,
            "fire": 30, "abandoned_object": 15, "stranded_person": 22,
            "crowd": 16, "deforestation": 18, "group": 20,
            "smoke": 24, "water_change": 12, "ecological_anomaly": 14,
        }.get(inp.object_class, 15)

        restricted_score = 20 if inp.in_restricted_zone else 5
        behaviour_score = int(inp.anomaly_score * 0.25) if inp.behaviour_anomaly else 5
        persistence_score = min(15, int(inp.duration_minutes * 0.5))
        confidence_score = int(inp.confidence * 8)
        group_score = min(10, inp.group_size * 2)
        historical_score = min(5, int(inp.historical_frequency * 5))

        total = (obj_score + restricted_score + behaviour_score +
                 persistence_score + confidence_score + group_score + historical_score)
        total = max(0, min(100, total))

        if total <= 30:
            level, priority = "low", "LOW"
        elif total <= 60:
            level, priority = "medium", "MEDIUM"
        elif total <= 80:
            level, priority = "high", "HIGH"
        else:
            level, priority = "critical", "CRITICAL"

        reasons = [
            f"object class ({inp.object_class}) contributes +{obj_score}",
            f"zone status: {'restricted' if inp.in_restricted_zone else 'unrestricted'} (+{restricted_score})",
        ]
        if behaviour_score > 10:
            reasons.append(f"behaviour anomaly score contributes +{behaviour_score}")
        if persistence_score > 5:
            reasons.append(f"extended duration in zone (+{persistence_score})")

        return RiskOutput(
            risk_score=total,
            risk_level=level,
            priority=priority,
            breakdown={
                "object_classification": obj_score,
                "restricted_zone": restricted_score,
                "behaviour_anomaly": behaviour_score,
                "persistence": persistence_score,
                "confidence": confidence_score,
                "group_size": group_score,
            },
            explanation=(
                f"Risk {total}/100 ({level.upper()}). "
                f"Primary factors: object class (+{obj_score}), "
                f"restricted zone (+{restricted_score}), "
                f"behaviour anomaly (+{behaviour_score})."
            ),
            reasons=reasons,
        )


# ─── Endurance Predictor ─────────────────────────────────────────────────────
class MockEndurancePredictor(BaseEndurancePredictor):
    """
    SIMULATION: Physics-inspired endurance prediction.
    REPLACE WITH: Random Forest/XGBoost trained on synthetic flight data.
    """

    async def predict(self, inp: EnduranceInput) -> EnduranceOutput:
        # Base drain: ~1.4% per minute at cruise
        base_drain = 1.4

        speed_factor = (inp.airspeed / 14.0) ** 1.5
        altitude_factor = 1.0 + (inp.altitude - 100) / 2000
        temp_factor = 1.0 + max(0, (inp.temperature - 30)) * 0.01
        wind_factor = inp.wind_factor
        payload_factor = 1.0 + inp.payload_weight * 0.02

        effective_drain = (base_drain * speed_factor * altitude_factor *
                           temp_factor * wind_factor * payload_factor)

        usable_pct = max(0, inp.battery_percentage - 8.0)
        total_remaining = usable_pct / effective_drain

        # Return reserve: time to fly back
        return_time = (inp.distance_from_base / 1000) / (inp.airspeed * 1.1) * 60
        safe_time = max(0, total_remaining - return_time)

        if safe_time > 20:
            risk = "low"
        elif safe_time > 10:
            risk = "medium"
        elif safe_time > 5:
            risk = "high"
        else:
            risk = "critical"

        # Predicted battery curve
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
            model_source="SIMULATION",
        )


# ─── Feasibility Predictor ────────────────────────────────────────────────────
class MockFeasibilityPredictor(BaseFeasibilityPredictor):
    """
    SIMULATION: Mission feasibility check using energy budget model.
    REPLACE WITH: Multi-factor ML model calibrated on real flight data.
    """

    async def predict(self, inp: FeasibilityInput) -> FeasibilityOutput:
        energy_per_km = 2.8
        to_km = inp.distance_to_target_m / 1000
        back_km = inp.return_distance_m / 1000

        mission_energy = ((to_km + back_km) * energy_per_km * inp.wind_factor
                          + inp.estimated_investigation_minutes * 1.4)
        return_reserve = 8.0
        usable = max(0, inp.battery_percentage - return_reserve)

        if usable >= mission_energy + 5:
            result = "FEASIBLE"
        elif usable >= mission_energy:
            result = "MARGINAL"
        else:
            result = "NOT_FEASIBLE"

        eta = datetime.utcnow() + timedelta(
            minutes=inp.estimated_investigation_minutes + to_km * 4)

        if result == "NOT_FEASIBLE":
            rec = ("Insufficient energy. Assign a drone with higher battery. "
                   f"Needed: {mission_energy:.1f}%, Available: {usable:.1f}%.")
        elif result == "MARGINAL":
            rec = ("Mission possible but tight. Consider reducing investigation time "
                   "or assigning a drone with more battery.")
        else:
            rec = ("Drone has sufficient energy to complete the mission "
                   f"with {usable - mission_energy:.1f}% energy margin.")

        return FeasibilityOutput(
            result=result,
            estimated_mission_energy=round(mission_energy, 1),
            available_usable_energy=round(usable, 1),
            required_return_reserve=return_reserve,
            predicted_completion_time=eta.strftime("%H:%M:%S"),
            confidence=round(random.uniform(0.88, 0.96), 3),
            recommendation=rec,
        )


# ─── Battery Health Predictor ─────────────────────────────────────────────────
class MockBatteryHealthPredictor(BaseBatteryHealthPredictor):
    """
    SIMULATION: Battery degradation model using empirical LiPo degradation curve.
    REPLACE WITH: RandomForest trained on battery cycle data.
    Degradation reference: typical UAV LiPo ~500 full cycles to 80% SoH.
    """

    async def predict(self, inp: BatteryHealthInput) -> BatteryHealthOutput:
        # Empirical degradation: ~0.04% SoH per cycle at nominal conditions
        base_degradation_per_cycle = 0.04

        # Temperature factor: >35°C accelerates degradation
        temp_factor = 1.0 + max(0, (inp.average_temperature - 35) * 0.02)

        # Deep discharge factor: >80% DoD accelerates degradation
        dod_factor = 1.0 + max(0, (inp.depth_of_discharge - 80) * 0.01)

        degradation_rate = base_degradation_per_cycle * temp_factor * dod_factor
        total_degradation = min(50, inp.cycle_count * degradation_rate)  # cap at 50% loss

        soh = max(50.0, 100.0 - total_degradation)
        estimated_remaining_mah = inp.nominal_capacity_mah * soh / 100
        remaining_cycles = max(0, int((soh - 70) / degradation_rate)) if soh > 70 else 0

        if soh >= 90:
            recommendation = "HEALTHY"
        elif soh >= 80:
            recommendation = "MONITOR"
        elif soh >= 70:
            recommendation = "REPLACE_SOON"
        else:
            recommendation = "REPLACE"

        return BatteryHealthOutput(
            state_of_health=round(soh, 1),
            estimated_remaining_capacity_mah=round(estimated_remaining_mah, 0),
            estimated_remaining_cycles=remaining_cycles,
            degradation_rate=round(degradation_rate, 4),
            recommendation=recommendation,
            confidence=round(random.uniform(0.82, 0.94), 3),
            model_source="SIMULATION",
        )
