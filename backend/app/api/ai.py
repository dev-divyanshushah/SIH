import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from app.ml.factory import (
    object_detector, behaviour_analyser, risk_scorer,
    endurance_predictor, feasibility_predictor,
)
from app.ml.base import (
    DetectionInput, BehaviourInput, RiskInput,
    EnduranceInput, FeasibilityInput,
)
from app.simulation.engine import simulation

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/detect")
async def detect_objects(inp: DetectionInput):
    result = await object_detector.detect(inp)
    return result.model_dump()


@router.post("/behaviour")
async def analyse_behaviour(inp: BehaviourInput):
    result = await behaviour_analyser.analyse(inp)
    return result.model_dump()


@router.post("/risk")
async def score_risk(inp: RiskInput):
    result = await risk_scorer.score(inp)
    return result.model_dump()


@router.post("/detections/list")
async def list_detections():
    """Return recent AI detections from simulation."""
    detections = []
    for anomaly in simulation.anomalies[-30:]:
        detections.append({
            "id": anomaly.id,
            "drone_id": anomaly.drone_id,
            "object_class": anomaly.object_class,
            "confidence": anomaly.confidence,
            "risk_score": anomaly.risk_score,
            "risk_level": anomaly.risk_level,
            "status": anomaly.status,
            "sector": anomaly.sector,
            "latitude": anomaly.lat,
            "longitude": anomaly.lon,
            "detected_at": anomaly.detected_at,
            "behaviour_type": anomaly.behaviour_type,
            "behaviour_description": anomaly.behaviour_description,
            "risk_breakdown": anomaly.risk_breakdown,
        })
    return detections
