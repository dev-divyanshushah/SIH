"""
ML Service Base Interfaces
===========================
These abstract base classes define the contract for all ML models used in PERSIST-AIR.

TO INTEGRATE A REAL MODEL:
1. Create a new class that inherits from the relevant base.
2. Implement the `predict` method using your model's inference logic.
3. Update the factory in ml_factory.py to return your class.
4. Set ML_SERVICE_URL in .env if using a remote model service.

The frontend NEVER calls ML services directly.
All inference goes through: Frontend → FastAPI Backend → ML Adapter → Model.
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


# ─── Input / Output schemas ──────────────────────────────────────────────────

class DetectionInput(BaseModel):
    frame_id: str
    drone_id: str
    image_path: Optional[str] = None
    image_base64: Optional[str] = None
    operational_mode: str = "security"

class DetectionOutput(BaseModel):
    detections: List[Dict[str, Any]]
    frame_id: str
    processing_time_ms: float


class BehaviourInput(BaseModel):
    object_id: str
    object_class: str
    track_history: List[Dict[str, Any]]  # [{lat, lon, t}]
    sector: str
    operational_mode: str = "security"

class BehaviourOutput(BaseModel):
    anomaly_detected: bool
    behaviour_type: Optional[str]
    anomaly_score: float  # 0-100
    confidence: float  # 0-1
    description: str
    normal_pattern: str
    observed_pattern: str


class RiskInput(BaseModel):
    object_class: str
    behaviour_anomaly: bool
    anomaly_score: float
    confidence: float
    sector: str
    in_restricted_zone: bool
    duration_minutes: float
    operational_mode: str = "security"

class RiskOutput(BaseModel):
    risk_score: int  # 0-100
    risk_level: str  # low/medium/high/critical
    breakdown: Dict[str, int]
    explanation: str


class EnduranceInput(BaseModel):
    drone_id: str
    battery_percentage: float
    battery_voltage: float
    current_consumption: float
    temperature: float
    airspeed: float
    altitude: float
    distance_from_base: float
    wind_factor: float = 1.0
    payload_weight: float = 0.0

class EnduranceOutput(BaseModel):
    remaining_endurance_minutes: float
    safe_mission_time: float
    return_reserve_minutes: float
    energy_risk: str  # low/medium/high/critical
    confidence: float
    predicted_battery_curve: List[Dict[str, float]]  # [{t, pct}]


class FeasibilityInput(BaseModel):
    drone_id: str
    battery_percentage: float
    distance_to_target_m: float
    estimated_investigation_minutes: float
    return_distance_m: float
    wind_factor: float = 1.0
    mission_priority: str = "medium"

class FeasibilityOutput(BaseModel):
    result: str  # FEASIBLE / MARGINAL / NOT_FEASIBLE
    estimated_mission_energy: float
    available_usable_energy: float
    required_return_reserve: float
    predicted_completion_time: str
    confidence: float
    recommendation: str


# ─── Abstract base classes ───────────────────────────────────────────────────

class BaseObjectDetector(ABC):
    @abstractmethod
    async def detect(self, inp: DetectionInput) -> DetectionOutput:
        ...

class BaseBehaviourAnalyser(ABC):
    @abstractmethod
    async def analyse(self, inp: BehaviourInput) -> BehaviourOutput:
        ...

class BaseRiskScorer(ABC):
    @abstractmethod
    async def score(self, inp: RiskInput) -> RiskOutput:
        ...

class BaseEndurancePredictor(ABC):
    @abstractmethod
    async def predict(self, inp: EnduranceInput) -> EnduranceOutput:
        ...

class BaseFeasibilityPredictor(ABC):
    @abstractmethod
    async def predict(self, inp: FeasibilityInput) -> FeasibilityOutput:
        ...
