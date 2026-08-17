from fastapi import APIRouter
from app.simulation.engine import simulation

router = APIRouter(prefix="/api", tags=["events-coverage-system"])


@router.get("/events")
async def get_events():
    return [e.to_dict() for e in reversed(simulation.events[-100:])]


@router.get("/coverage")
async def get_coverage():
    drones = list(simulation.drones.values())
    active = [d for d in drones if d.status == "active"]
    return {
        "coverage_percentage": round(simulation.coverage_percentage, 2),
        "uncovered_percentage": round(100 - simulation.coverage_percentage, 2),
        "predicted_continuity": 99.1,
        "active_drones": len(active),
        "zones": [
            {"id": "ZONE-A", "lat": 28.6239, "lon": 77.2010, "radius": 800, "drone": "PA-01", "coverage": 98.2},
            {"id": "ZONE-B", "lat": 28.6039, "lon": 77.2190, "radius": 700, "drone": "PA-02", "coverage": 96.7},
            {"id": "ZONE-C", "lat": 28.6139, "lon": 77.1990, "radius": 900, "drone": "PA-04", "coverage": 97.9},
            {"id": "ZONE-D", "lat": 28.5989, "lon": 77.1990, "radius": 750, "drone": "PA-05", "coverage": 95.4},
        ],
        "active_handover": simulation.active_handover,
    }


@router.get("/simulation/state")
async def get_simulation_state():
    drones = list(simulation.drones.values())
    active = [d for d in drones if d.status == "active"]
    returning = [d for d in drones if d.status == "returning"]
    charging = [d for d in drones if d.status == "charging"]
    available = [d for d in drones if d.status == "available"]
    critical = [d for d in drones if d.status == "critical"]
    avg_battery = sum(d.battery_pct for d in drones) / len(drones) if drones else 0
    return {
        "running": simulation.running,
        "tick": simulation.tick,
        "speed_multiplier": simulation.speed_multiplier,
        "operational_mode": simulation.operational_mode,
        "demo_mode": simulation.demo_mode,
        "active_drones": len(active),
        "available_drones": len(available),
        "charging_drones": len(charging),
        "returning_drones": len(returning),
        "critical_drones": len(critical),
        "total_drones": len(drones),
        "coverage_percentage": round(simulation.coverage_percentage, 2),
        "average_battery": round(avg_battery, 1),
        "active_anomalies": len([a for a in simulation.anomalies if a.status == "detected"]),
        "total_events": len(simulation.events),
        "active_handover": simulation.active_handover,
    }


@router.post("/simulation/start")
async def start_simulation():
    simulation.start()
    simulation.add_event("system", None, "Simulation started", "PERSIST-AIR simulation engine running.", "low")
    return {"status": "running"}


@router.post("/simulation/pause")
async def pause_simulation():
    simulation.pause()
    return {"status": "paused"}


@router.post("/simulation/reset")
async def reset_simulation():
    simulation.reset()
    return {"status": "reset"}


@router.post("/simulation/speed")
async def set_speed(data: dict):
    multiplier = data.get("multiplier", 1)
    simulation.set_speed(multiplier)
    return {"speed_multiplier": simulation.speed_multiplier}


@router.post("/simulation/demo")
async def start_demo():
    simulation.start_demo()
    return {"status": "demo_started"}


@router.post("/simulation/mode")
async def set_mode(data: dict):
    mode = data.get("mode", "security")
    if mode not in ("security", "humanitarian", "environmental"):
        from fastapi import HTTPException
        raise HTTPException(400, "Invalid mode")
    simulation.operational_mode = mode
    for d in simulation.drones.values():
        d.operational_mode = mode
    simulation.add_event("system", None,
                         f"Operational mode changed to {mode.upper()}",
                         f"All drones now operating in {mode} mode.", "low")
    return {"mode": mode}


@router.get("/system/status")
async def system_status():
    import datetime
    drones = list(simulation.drones.values())
    avg_battery = sum(d.battery_pct for d in drones) / len(drones) if drones else 0
    return {
        "status": "online",
        "version": "1.0.0",
        "environment": "development",
        "simulation_running": simulation.running,
        "drones_online": len([d for d in drones if d.status != "offline"]),
        "total_drones": len(drones),
        "active_anomalies": len([a for a in simulation.anomalies if a.status == "detected"]),
        "coverage": round(simulation.coverage_percentage, 2),
        "average_battery": round(avg_battery, 1),
        "operational_mode": simulation.operational_mode,
        "server_time": datetime.datetime.utcnow().isoformat() + "Z",
        "ws_connections": 0,  # updated via manager
    }
