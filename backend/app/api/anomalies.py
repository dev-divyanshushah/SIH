from fastapi import APIRouter
from app.simulation.engine import simulation

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])

@router.get("")
async def get_anomalies():
    return [a.to_dict() for a in simulation.anomalies]

@router.get("/{anomaly_id}")
async def get_anomaly(anomaly_id: str):
    for a in simulation.anomalies:
        if a.id == anomaly_id:
            return a.to_dict()
    from fastapi import HTTPException
    raise HTTPException(404, "Anomaly not found")

@router.post("/{anomaly_id}/verify")
async def verify_anomaly(anomaly_id: str, data: dict):
    action = data.get("action", "confirm")  # confirm / dismiss
    for a in simulation.anomalies:
        if a.id == anomaly_id:
            if action == "confirm":
                a.status = "verified"
                simulation.add_event("verification_confirmed", a.drone_id,
                                     f"Anomaly {anomaly_id} confirmed by operator",
                                     f"Human verification: CONFIRMED", "high",
                                     a.lat, a.lon, a.sector, anomaly_id)
            elif action == "dismiss":
                a.status = "dismissed"
                simulation.add_event("verification_dismissed", a.drone_id,
                                     f"Anomaly {anomaly_id} dismissed",
                                     "Human verification: DISMISSED — False positive", "low",
                                     a.lat, a.lon, a.sector, anomaly_id)
            return {"status": "ok", "anomaly": a.to_dict()}
    from fastapi import HTTPException
    raise HTTPException(404, "Anomaly not found")
