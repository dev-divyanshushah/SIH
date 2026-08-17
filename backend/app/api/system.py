import datetime as _dt
from fastapi import APIRouter, HTTPException
from app.simulation.engine import simulation

router = APIRouter(prefix="/api", tags=["events-coverage-system"])


@router.get("/events")
async def get_events():
    return [e.to_dict() for e in reversed(simulation.events[-100:])]


@router.get("/coverage")
async def get_coverage():
    """Dynamic coverage calculated from actual drone positions."""
    zones = simulation.get_coverage_zones()
    active = [d for d in simulation.drones.values()
              if d.status in ("active", "investigating", "patrolling")]
    return {
        "coverage_percentage": round(simulation.coverage_percentage, 2),
        "uncovered_percentage": round(100 - simulation.coverage_percentage, 2),
        "predicted_continuity": round(
            simulation.coverage_percentage * 0.995 +
            len(active) * 0.5, 1
        ),
        "active_drones": len(active),
        "zones": zones,
        "active_handover": simulation.active_handover,
    }


@router.get("/fleet/status")
async def get_fleet_status():
    """Comprehensive fleet status summary."""
    drones = list(simulation.drones.values())
    by_status = {}
    for d in drones:
        by_status.setdefault(d.status, []).append(d.id)

    return {
        "total_drones": len(drones),
        "by_status": by_status,
        "average_battery": round(
            sum(d.battery_pct for d in drones) / len(drones), 1
        ) if drones else 0,
        "average_health": round(
            sum(d.health_score for d in drones) / len(drones), 1
        ) if drones else 0,
        "coverage_percentage": round(simulation.coverage_percentage, 2),
        "active_handover": simulation.active_handover is not None,
        "drones": [d.to_dict() for d in drones],
    }


@router.get("/simulation/state")
async def get_simulation_state():
    drones = list(simulation.drones.values())
    active = [d for d in drones if d.status == "active"]
    investigating = [d for d in drones if d.status == "investigating"]
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
        "active_drones": len(active) + len(investigating),
        "investigating_drones": len(investigating),
        "available_drones": len(available),
        "charging_drones": len(charging),
        "returning_drones": len(returning),
        "critical_drones": len(critical),
        "total_drones": len(drones),
        "coverage_percentage": round(simulation.coverage_percentage, 2),
        "average_battery": round(avg_battery, 1),
        "active_anomalies": len([a for a in simulation.anomalies
                                  if a.status in ("detected", "under_investigation")]),
        "total_events": len(simulation.events),
        "active_handover": simulation.active_handover,
        "simulated_mission_time": simulation.simulated_mission_time,
    }


@router.post("/simulation/start")
async def start_simulation():
    simulation.start()
    simulation.add_event("system", None, "Simulation started",
                         "PERSIST-AIR simulation engine running.", "low")
    return {"status": "running"}


@router.post("/simulation/pause")
async def pause_simulation():
    simulation.pause()
    return {"status": "paused"}


@router.post("/simulation/reset")
async def reset_simulation():
    was_running = simulation.running
    simulation.reset()
    if was_running:
        simulation.start()
    return {"status": "reset"}


@router.post("/simulation/speed")
async def set_speed(data: dict):
    multiplier = data.get("multiplier", 1)
    simulation.set_speed(multiplier)
    return {"speed_multiplier": simulation.speed_multiplier}


@router.post("/simulation/demo")
async def start_demo():
    simulation.start_demo()
    return {"status": "demo_started", "steps": 11}


@router.post("/simulation/mode")
async def set_mode(data: dict):
    mode = data.get("mode", "security")
    if mode not in ("security", "humanitarian", "environmental"):
        raise HTTPException(400, "Invalid mode. Use: security, humanitarian, environmental")
    simulation.operational_mode = mode
    for d in simulation.drones.values():
        d.operational_mode = mode
    simulation.add_event("system", None,
                         f"Operational mode changed to {mode.upper()}",
                         f"All drones now operating in {mode} mode.", "low")
    return {"mode": mode}


@router.post("/simulation/scenario")
async def run_scenario(data: dict):
    """
    Run a predefined simulation scenario.
    Available: normal_patrol, human_anomaly, multiple_anomalies,
               low_battery_handover, drone_failure, communication_loss,
               humanitarian_emergency, environmental_event, long_duration_persistence
    """
    scenario = data.get("scenario", "normal_patrol")
    result = simulation.run_scenario(scenario)
    return result


@router.get("/system/status")
async def system_status():
    drones = list(simulation.drones.values())
    avg_battery = sum(d.battery_pct for d in drones) / len(drones) if drones else 0
    return {
        "status": "online",
        "version": "1.0.0",
        "environment": "development",
        "label": "PERSIST-AIR — AI-Powered Persistent Aerial Intelligence",
        "simulation_running": simulation.running,
        "drones_online": len([d for d in drones if d.status != "offline"]),
        "total_drones": len(drones),
        "active_anomalies": len([a for a in simulation.anomalies
                                  if a.status in ("detected", "under_investigation")]),
        "coverage": round(simulation.coverage_percentage, 2),
        "average_battery": round(avg_battery, 1),
        "operational_mode": simulation.operational_mode,
        "simulated_mission_time": simulation.simulated_mission_time,
        "ml_mode": "REAL_MODEL or SIMULATION (see startup logs)",
        "server_time": _dt.datetime.utcnow().isoformat() + "Z",
    }
