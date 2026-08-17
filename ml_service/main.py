"""
PERSIST-AIR ML Service
========================
Standalone FastAPI service for ML inference on port 8001.
This service handles the heavy ML inference (especially object detection with YOLO).

The backend calls this service when ML_SERVICE_URL is set and reachable.
Falls back to internal mocks if this service is unavailable.

Usage:
    cd ml_service
    pip install -r requirements.txt
    python -m uvicorn main:app --reload --port 8001

Object Detection:
    - Uses YOLOv8n pretrained on COCO for person/vehicle/motorcycle detection
    - COCO categories relevant to PERSIST-AIR: person, car, truck, motorcycle, bicycle
    - For fire/smoke detection: requires custom training (see object_detection/training.py)
    - Clearly labeled: PRETRAINED_COCO / CUSTOM_TRAINED / SIMULATION
"""
import time
import uuid
import random
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

logging.basicConfig(level="INFO")
logger = logging.getLogger("persist-air.ml-service")

app = FastAPI(
    title="PERSIST-AIR ML Service",
    description="Object detection, anomaly scoring, energy prediction inference",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Try to load YOLO ────────────────────────────────────────────────────────
YOLO_MODEL = None
YOLO_AVAILABLE = False

try:
    from ultralytics import YOLO
    # YOLOv8n is the smallest model — runs adequately on CPU
    YOLO_MODEL = YOLO("yolov8n.pt")  # Downloads automatically on first run
    YOLO_AVAILABLE = True
    logger.info("✓ YOLOv8n loaded (pretrained on COCO)")
    logger.info("  Note: COCO classes — person, vehicle types detected")
    logger.info("  Note: Fire/smoke requires custom fine-tuning")
except ImportError:
    logger.warning("ultralytics not installed — using simulation detector")
    logger.warning("Install: pip install ultralytics")
except Exception as e:
    logger.warning(f"YOLO load failed: {e} — using simulation detector")


# ─── Schemas ──────────────────────────────────────────────────────────────────
class DetectionRequest(BaseModel):
    frame_id: str
    drone_id: str
    image_base64: Optional[str] = None
    image_path: Optional[str] = None
    operational_mode: str = "security"
    confidence_threshold: float = 0.4
    max_resolution: int = 640  # CPU-friendly

class Detection(BaseModel):
    id: str
    object_class: str
    confidence: float
    bbox: List[int]
    track_id: Optional[int] = None
    risk: str
    timestamp: str

class DetectionResponse(BaseModel):
    detections: List[Detection]
    frame_id: str
    processing_time_ms: float
    model_source: str
    drone_id: str


class AnomalyRequest(BaseModel):
    object_class: str
    duration_minutes: float
    group_size: int = 1
    time_of_day: float = 12.0
    day_of_week: int = 1
    in_restricted_zone: bool = False
    speed_variance: float = 0.0
    direction_changes: int = 0
    distance_from_normal_area: float = 0.0

class EnergyRequest(BaseModel):
    battery_percentage: float
    battery_voltage: float
    current_consumption: float
    temperature: float
    airspeed: float
    altitude: float
    distance_from_base: float
    wind_factor: float = 1.0
    payload_weight: float = 0.0


# ─── COCO class mapping ───────────────────────────────────────────────────────
COCO_TO_PERSIST = {
    "person": "person",
    "car": "vehicle",
    "truck": "vehicle",
    "bus": "vehicle",
    "motorcycle": "motorcycle",
    "bicycle": "vehicle",
    "backpack": "abandoned_object",
    "suitcase": "abandoned_object",
    "crowd": "group",
}

HIGH_RISK_CLASSES = {"vehicle", "fire", "smoke", "stranded_person"}

SIMULATION_OBJECTS = {
    "security": ["vehicle", "person", "motorcycle", "group", "abandoned_object"],
    "humanitarian": ["stranded_person", "crowd", "fire", "smoke"],
    "environmental": ["deforestation", "smoke", "water_change", "ecological_anomaly"],
}


def _simulate_detection(mode: str) -> List[Dict]:
    """Simulation fallback when YOLO is unavailable."""
    candidates = SIMULATION_OBJECTS.get(mode, SIMULATION_OBJECTS["security"])
    n = random.choices([0, 1, 2, 3], weights=[40, 40, 15, 5])[0]
    return [{
        "id": uuid.uuid4().hex[:8],
        "class": random.choice(candidates),
        "confidence": round(random.uniform(0.72, 0.98), 3),
        "bbox": [random.randint(50, 400), random.randint(50, 300),
                 random.randint(40, 200), random.randint(40, 150)],
        "track_id": random.randint(1000, 9999),
        "risk": "high" if random.random() < 0.3 else "medium",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    } for _ in range(n)]


def _yolo_detect(image_base64: str, confidence_threshold: float) -> List[Dict]:
    """Run YOLO inference on base64-encoded image."""
    import base64
    import io
    from PIL import Image as PILImage
    import numpy as np

    img_data = base64.b64decode(image_base64)
    img = PILImage.open(io.BytesIO(img_data)).convert("RGB")
    img_np = np.array(img)

    results = YOLO_MODEL.predict(img_np, conf=confidence_threshold, verbose=False)
    detections = []

    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            cls_name = YOLO_MODEL.names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
            persist_class = COCO_TO_PERSIST.get(cls_name, cls_name)
            detections.append({
                "id": uuid.uuid4().hex[:8],
                "class": persist_class,
                "confidence": round(conf, 3),
                "bbox": [x1, y1, x2 - x1, y2 - y1],
                "track_id": None,
                "risk": "high" if persist_class in HIGH_RISK_CLASSES else "medium",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })

    return detections


# ─── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "service": "PERSIST-AIR ML Service",
        "port": 8001,
        "yolo_available": YOLO_AVAILABLE,
        "model": "YOLOv8n (COCO)" if YOLO_AVAILABLE else "SIMULATION",
        "note": "Fire/smoke detection requires custom fine-tuning on specialized dataset",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "yolo": YOLO_AVAILABLE}


@app.post("/detect", response_model=DetectionResponse)
async def detect_objects(req: DetectionRequest):
    t0 = time.time()

    if YOLO_AVAILABLE and req.image_base64:
        try:
            detections_raw = _yolo_detect(req.image_base64, req.confidence_threshold)
            model_source = "PRETRAINED_YOLOV8N_COCO"
            note = "Fire/smoke requires custom training"
        except Exception as e:
            logger.warning(f"YOLO inference failed: {e}. Falling back to simulation.")
            detections_raw = _simulate_detection(req.operational_mode)
            model_source = "SIMULATION (YOLO_FALLBACK)"
    else:
        detections_raw = _simulate_detection(req.operational_mode)
        model_source = "SIMULATION"

    elapsed = (time.time() - t0) * 1000
    detections = [Detection(**d) for d in detections_raw]

    return DetectionResponse(
        detections=detections,
        frame_id=req.frame_id,
        processing_time_ms=round(elapsed, 2),
        model_source=model_source,
        drone_id=req.drone_id,
    )


@app.post("/anomaly/score")
async def score_anomaly(req: AnomalyRequest):
    """
    Score an observation using the anomaly model.
    Falls back to simulation if model not loaded.
    """
    # Try to load the trained model
    model_path = os.path.join("..", "models", "anomaly_model", "model.joblib")

    try:
        import os
        import joblib
        import numpy as np
        if os.path.exists(model_path):
            data = joblib.load(model_path)
            model = data["model"]
            scaler = data.get("scaler")
            features = np.array([[
                req.duration_minutes, req.group_size, req.time_of_day,
                req.day_of_week, float(req.in_restricted_zone),
                req.speed_variance, float(req.direction_changes),
                req.distance_from_normal_area,
            ]])
            if scaler:
                features = scaler.transform(features)
            score = float(model.decision_function(features)[0])
            pred = int(model.predict(features)[0])
            anomaly_score = max(0, min(100, (-score + 0.5) / 1.0 * 100))
            return {
                "anomaly_detected": pred == -1,
                "anomaly_score": round(anomaly_score, 1),
                "anomaly_probability": round((-score + 0.3) / 0.6, 3),
                "model_source": "REAL_MODEL (Synthetic Training Data)",
            }
    except Exception:
        pass

    # Simulation fallback
    score = (
        (20 if req.in_restricted_zone else 0) +
        min(30, req.duration_minutes * 0.5) +
        (15 if req.time_of_day < 6 or req.time_of_day > 22 else 0) +
        min(20, req.group_size * 3) +
        min(15, req.speed_variance * 1000)
    ) + random.uniform(-5, 5)
    score = max(0, min(100, score))
    return {
        "anomaly_detected": score > 40,
        "anomaly_score": round(score, 1),
        "anomaly_probability": round(score / 100, 3),
        "model_source": "SIMULATION",
    }


@app.post("/energy/predict")
async def predict_energy(req: EnergyRequest):
    """Energy endurance prediction — uses trained model or simulation."""
    model_path = os.path.join("..", "models", "energy_model", "model.joblib")

    try:
        import os
        import joblib
        import numpy as np
        if os.path.exists(model_path):
            data = joblib.load(model_path)
            model = data["model"]
            scaler = data.get("scaler")
            features = np.array([[
                req.battery_percentage, req.battery_voltage, req.current_consumption,
                req.temperature, req.airspeed, req.altitude,
                req.distance_from_base, req.wind_factor, req.payload_weight,
            ]])
            if scaler:
                features = scaler.transform(features)
            endurance = float(model.predict(features)[0])
            endurance = max(0, endurance)
            return {
                "remaining_endurance_minutes": round(endurance, 1),
                "model_source": "REAL_MODEL (Synthetic Training Data)",
            }
    except Exception:
        pass

    # Simulation
    drain = 1.4 * (req.airspeed / 14.0) ** 1.5 * req.wind_factor
    endurance = max(0, (req.battery_percentage - 8) / drain)
    return {
        "remaining_endurance_minutes": round(endurance, 1),
        "model_source": "SIMULATION",
    }
