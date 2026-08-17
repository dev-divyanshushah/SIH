from fastapi import APIRouter
from app.simulation.engine import simulation

router = APIRouter(prefix="/api/missions", tags=["missions"])

@router.get("")
async def get_missions():
    return simulation.missions

@router.get("/{mission_id}")
async def get_mission(mission_id: str):
    for m in simulation.missions:
        if m["id"] == mission_id:
            return m
    from fastapi import HTTPException
    raise HTTPException(404, "Mission not found")

@router.post("")
async def create_mission(data: dict):
    import uuid
    mission = {
        "id": f"MSN-{uuid.uuid4().hex[:6].upper()}",
        "status": "planned",
        **data,
        "created_at": __import__('datetime').datetime.utcnow().isoformat() + "Z",
    }
    simulation.missions.append(mission)
    simulation.add_event("mission_started", data.get("assigned_drone_id"),
                         f"Mission {mission['id']} created", data.get("name", "New mission"), "low")
    return mission
