from fastapi import APIRouter
from app.simulation.engine import simulation

router = APIRouter(prefix="/api/drones", tags=["drones"])

@router.get("")
async def get_drones():
    return [d.to_dict() for d in simulation.drones.values()]

@router.get("/{drone_id}")
async def get_drone(drone_id: str):
    d = simulation.drones.get(drone_id.upper())
    if not d:
        from fastapi import HTTPException
        raise HTTPException(404, "Drone not found")
    return d.to_dict()

@router.get("/{drone_id}/telemetry")
async def get_drone_telemetry(drone_id: str):
    d = simulation.drones.get(drone_id.upper())
    if not d:
        from fastapi import HTTPException
        raise HTTPException(404, "Drone not found")
    return {
        "drone_id": d.id,
        "battery_history": d.battery_history,
        "speed_history": d.speed_history,
        "altitude_history": d.altitude_history,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z",
    }
