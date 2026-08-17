"""
ML Service Base Interfaces
===========================
Abstract base classes that define the contract for all ML models in PERSIST-AIR.

Architecture:
  Frontend → FastAPI Backend → ML Adapter (factory.py) → Model (real or mock)

To integrate a real model:
1. Create a class inheriting from the relevant base.
2. Implement the abstract method.
3. Update factory.py to return your class.
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
    model_source: str = "SIMULATION"   # REAL_MODEL | SIMULATION


class BehaviourInput(BaseModel):
    object_id: str
    object_class: str
    track_history: List[Dict[str, Any]]   # [{lat, lon, t}]
    sector: str
    time_of_day: float = 12.0             # 0-24 hours
    day_of_week: int = 1                  # 0=Mon
    duration_minutes: float = 0.0
    group_size: int = 1
    in_restricted_zone: bool = False
    operational_mode: str = "security"

class BehaviourOutput(BaseModel):
    anomaly_detected: bool
    behaviour_type: Optional[str]
    anomaly_score: float       # 0-100
    anomaly_probability: float # 0-1
    confidence: float          # 0-1
    anomaly_type: str
    description: str
    normal_pattern: str
    observed_pattern: str
    reasons: List[str]
    model_source: str = "SIMULATION"


class RiskInput(BaseModel):
    object_class: str
    behaviour_anomaly: bool
    anomaly_score: float
    confidence: float
    sector: str
    in_restricted_zone: bool
    duration_minutes: float
    group_size: int = 1
    historical_frequency: float = 0.0
    operational_mode: str = "security"

class RiskOutput(BaseModel):
    risk_score: int    # 0-100
    risk_level: str    # low/medium/high/critical
    priority: str      # LOW|MEDIUM|HIGH|CRITICAL
    breakdown: Dict[str, int]
    explanation: str
    reasons: List[str]


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
    energy_risk: str   # low/medium/high/critical
    confidence: float
    predicted_battery_curve: List[Dict[str, float]]  # [{t, pct}]
    model_source: str = "SIMULATION"


class FeasibilityInput(BaseModel):
    drone_id: str
    battery_percentage: float
    distance_to_target_m: float
    estimated_investigation_minutes: float
    return_distance_m: float
    wind_factor: float = 1.0
    mission_priority: str = "medium"

class FeasibilityOutput(BaseModel):
    result: str   # FEASIBLE / MARGINAL / NOT_FEASIBLE
    estimated_mission_energy: float
    available_usable_energy: float
    required_return_reserve: float
    predicted_completion_time: str
    confidence: float
    recommendation: str


class BatteryHealthInput(BaseModel):
    drone_id: str
    cycle_count: int
    average_temperature: float = 28.0
    depth_of_discharge: float = 80.0   # % average DoD
    current_capacity_mah: float = 5200.0
    nominal_capacity_mah: float = 5200.0
    voltage_sag: float = 0.3           # voltage drop under load

class BatteryHealthOutput(BaseModel):
    state_of_health: float             # 0-100 %
    estimated_remaining_capacity_mah: float
    estimated_remaining_cycles: int
    degradation_rate: float            # % per cycle
    recommendation: str                # HEALTHY|MONITOR|REPLACE_SOON|REPLACE
    confidence: float
    model_source: str = "SIMULATION"


# ─── Abstract base classes ───────────────────────────────────────────────────

class BaseObjectDetector(ABC):
    @abstractmethod
    async def detect(self, inp: DetectionInput) -> DetectionOutput: ...

class BaseBehaviourAnalyser(ABC):
    @abstractmethod
    async def analyse(self, inp: BehaviourInput) -> BehaviourOutput: ...

class BaseRiskScorer(ABC):
    @abstractmethod
    async def score(self, inp: RiskInput) -> RiskOutput: ...

class BaseEndurancePredictor(ABC):
    @abstractmethod
    async def predict(self, inp: EnduranceInput) -> EnduranceOutput: ...

class BaseFeasibilityPredictor(ABC):
    @abstractmethod
    async def predict(self, inp: FeasibilityInput) -> FeasibilityOutput: ...

class BaseBatteryHealthPredictor(ABC):
    @abstractmethod
    async def predict(self, inp: BatteryHealthInput) -> BatteryHealthOutput: ...
