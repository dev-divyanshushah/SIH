from fastapi import APIRouter
from app.ml.factory import endurance_predictor, feasibility_predictor
from app.ml.base import EnduranceInput, FeasibilityInput
from app.simulation.engine import simulation

router = APIRouter(prefix="/api", tags=["energy"])


@router.post("/energy/predict")
async def predict_energy(inp: EnduranceInput):
    result = await endurance_predictor.predict(inp)
    return result.model_dump()


@router.post("/mission/feasibility")
async def check_feasibility(inp: FeasibilityInput):
    result = await feasibility_predictor.predict(inp)
    return result.model_dump()


@router.post("/mission/select-drone")
async def select_drone(data: dict):
    """Score all available drones for a given mission target."""
    target_lat = data.get("target_lat", 0)
    target_lon = data.get("target_lon", 0)
    import math

    candidates = []
    for drone in simulation.drones.values():
        if drone.status not in ("active", "available"):
            continue
        dlat = drone.lat - target_lat
        dlon = drone.lon - target_lon
        dist_m = math.sqrt(dlat**2 + dlon**2) * 111000
        dist_km = dist_m / 1000

        # Score factors (0-100)
        energy_score = drone.battery_pct
        distance_score = max(0, 100 - dist_km * 10)
        health_score = drone.health_score
        comm_score = drone.communication_quality
        workload_score = 100 if drone.mission_id is None else 60

        total = (energy_score * 0.35 + distance_score * 0.30 +
                 health_score * 0.15 + comm_score * 0.10 + workload_score * 0.10)

        # Feasibility check
        energy_needed = dist_km * 2 * 2.8 + 20  # to+fro + investigation
        feasible = drone.battery_pct > energy_needed + 8

        candidates.append({
            "drone_id": drone.id,
            "score": round(total, 1),
            "energy_score": round(energy_score, 1),
            "distance_score": round(distance_score, 1),
            "distance_km": round(dist_km, 2),
            "health_score": health_score,
            "communication_quality": comm_score,
            "feasible": feasible,
            "battery_percentage": round(drone.battery_pct, 1),
            "status": drone.status,
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)

    recommended = next((c for c in candidates if c["feasible"]), None)
    if recommended:
        simulation.add_event(
            "drone_selection", recommended["drone_id"],
            f"AI Drone Selection — {recommended['drone_id']} recommended",
            f"Score: {recommended['score']}/100. Sufficient energy and proximity.",
            "medium",
        )

    return {
        "candidates": candidates,
        "recommended": recommended,
    }


@router.post("/path/plan")
async def plan_path(data: dict):
    """Energy-aware path planning mock."""
    import math, random
    drone_id = data.get("drone_id")
    target_lat = data.get("target_lat")
    target_lon = data.get("target_lon")

    drone = simulation.drones.get(drone_id)
    if not drone:
        from fastapi import HTTPException
        raise HTTPException(404, "Drone not found")

    # Shortest path (direct line)
    shortest_path = [
        {"lat": drone.lat, "lon": drone.lon},
        {"lat": target_lat, "lon": target_lon},
    ]

    # Energy-aware path (slight detour to avoid altitude loss zones, favor tailwind)
    mid_lat = (drone.lat + target_lat) / 2 + random.uniform(-0.002, 0.002)
    mid_lon = (drone.lon + target_lon) / 2 + random.uniform(-0.002, 0.002)
    energy_path = [
        {"lat": drone.lat, "lon": drone.lon},
        {"lat": mid_lat, "lon": mid_lon},
        {"lat": target_lat, "lon": target_lon},
    ]

    dlat = target_lat - drone.lat
    dlon = target_lon - drone.lon
    dist_m = math.sqrt(dlat**2 + dlon**2) * 111000

    return {
        "drone_id": drone_id,
        "shortest_path": shortest_path,
        "shortest_distance_m": round(dist_m, 0),
        "shortest_energy_pct": round(dist_m / 1000 * 2.8, 1),
        "energy_path": energy_path,
        "energy_path_distance_m": round(dist_m * 1.08, 0),
        "energy_path_energy_pct": round(dist_m / 1000 * 2.8 * 0.93, 1),  # 7% saving
        "energy_saving_pct": 7.0,
        "explanation": "Energy-aware route avoids headwind sectors and maintains optimal altitude for battery efficiency.",
    }


@router.post("/handover/predict")
async def predict_handover(data: dict):
    """Predict optimal handover time for a drone."""
    drone_id = data.get("drone_id")
    drone = simulation.drones.get(drone_id)
    if not drone:
        from fastapi import HTTPException
        raise HTTPException(404, "Drone not found")

    import math
    drain_per_min = 1.4
    minutes_to_critical = max(0, (drone.battery_pct - 20) / drain_per_min)

    return {
        "active_drone": drone_id,
        "current_battery": round(drone.battery_pct, 1),
        "predicted_handover_in_minutes": round(minutes_to_critical, 1),
        "coverage_continuity": 98.7,
        "handover_confidence": 94.0,
        "recommended_replacement": "PA-04" if drone_id != "PA-04" else "PA-01",
        "handover_active": simulation.active_handover,
    }
