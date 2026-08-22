"""
PERSIST-AIR Simulation Engine
===============================
Simulates realistic multi-drone behavior:
- Gradual battery depletion (physics-based)
- Route-following movement with heading calculation
- Anomaly event generation (all 3 modes)
- General predictive handover engine (any drone pair)
- Dynamic coverage calculation from drone positions
- Accelerated simulated mission time
- 9 scenario modes
- Anomaly investigation_drone_id properly tracked
"""
import asyncio
import math
import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# ─── Base location: India-Pakistan Border Region ────────────────────────────────
BASE_LAT = 29.5000
BASE_LON = 73.5000

DRONE_CONFIGS = [
    {
        "id": "PA-01",
        "name": "PERSIST ALPHA-01 (CENTRAL)",
        "home_lat": BASE_LAT,
        "home_lon": BASE_LON,
        "start_battery": 94.0,
        "route": [
            (BASE_LAT + 0.003, BASE_LON - 0.003),
            (BASE_LAT + 0.003, BASE_LON + 0.003),
            (BASE_LAT - 0.003, BASE_LON + 0.003),
            (BASE_LAT - 0.003, BASE_LON - 0.003),
        ],
        "status": "active",
    },
    {
        "id": "PA-02",
        "name": "PERSIST ALPHA-02 (NORTH)",
        "home_lat": BASE_LAT + 0.012,
        "home_lon": BASE_LON,
        "start_battery": 89.0,
        "route": [
            (BASE_LAT + 0.015, BASE_LON - 0.003),
            (BASE_LAT + 0.015, BASE_LON + 0.003),
            (BASE_LAT + 0.009, BASE_LON + 0.003),
            (BASE_LAT + 0.009, BASE_LON - 0.003),
        ],
        "status": "active",
    },
    {
        "id": "PA-03",
        "name": "PERSIST ALPHA-03 (EAST)",
        "home_lat": BASE_LAT,
        "home_lon": BASE_LON + 0.012,
        "start_battery": 82.0,
        "route": [
            (BASE_LAT + 0.003, BASE_LON + 0.015),
            (BASE_LAT - 0.003, BASE_LON + 0.015),
            (BASE_LAT - 0.003, BASE_LON + 0.009),
            (BASE_LAT + 0.003, BASE_LON + 0.009),
        ],
        "status": "active",
    },
    {
        "id": "PA-04",
        "name": "PERSIST ALPHA-04 (WEST)",
        "home_lat": BASE_LAT,
        "home_lon": BASE_LON - 0.012,
        "start_battery": 87.0,
        "route": [
            (BASE_LAT + 0.003, BASE_LON - 0.009),
            (BASE_LAT - 0.003, BASE_LON - 0.009),
            (BASE_LAT - 0.003, BASE_LON - 0.015),
            (BASE_LAT + 0.003, BASE_LON - 0.015),
        ],
        "status": "active",
    },
    {
        "id": "PA-05",
        "name": "PERSIST ALPHA-05 (SOUTH)",
        "home_lat": BASE_LAT - 0.012,
        "home_lon": BASE_LON,
        "start_battery": 68.0,
        "route": [
            (BASE_LAT - 0.009, BASE_LON - 0.003),
            (BASE_LAT - 0.009, BASE_LON + 0.003),
            (BASE_LAT - 0.015, BASE_LON + 0.003),
            (BASE_LAT - 0.015, BASE_LON - 0.003),
        ],
        "status": "active",
    },
]

SECTOR_MAP = {
    "CENTRAL": (BASE_LAT, BASE_LON),
    "NORTH": (BASE_LAT + 0.012, BASE_LON),
    "EAST": (BASE_LAT, BASE_LON + 0.012),
    "WEST": (BASE_LAT, BASE_LON - 0.012),
    "SOUTH": (BASE_LAT - 0.012, BASE_LON),
}

# Coverage radius for each drone in degrees (~1.2km / 0.011 degrees)
COVERAGE_RADIUS_DEG = 0.011


@dataclass
class SimDrone:
    id: str
    name: str
    home_lat: float
    home_lon: float
    lat: float
    lon: float
    altitude: float = 120.0
    airspeed: float = 14.0
    heading: float = 0.0
    battery_pct: float = 100.0
    battery_voltage: float = 22.2
    current_amp: float = 18.5
    battery_temp: float = 28.0
    status: str = "active"
    mission_id: Optional[str] = None
    mission_type: Optional[str] = None
    investigation_target_lat: Optional[float] = None
    investigation_target_lon: Optional[float] = None
    route: List = field(default_factory=list)
    route_idx: int = 0
    communication_quality: int = 98
    health_score: int = 100
    operational_mode: str = "security"
    battery_history: List[float] = field(default_factory=list)
    speed_history: List[float] = field(default_factory=list)
    altitude_history: List[float] = field(default_factory=list)
    # Cycle tracking for battery health
    cycle_count: int = field(default_factory=lambda: random.randint(20, 120))

    @property
    def distance_from_base(self) -> float:
        dlat = self.lat - self.home_lat
        dlon = self.lon - self.home_lon
        return math.sqrt(dlat**2 + dlon**2) * 111000  # metres

    @property
    def estimated_flight_time(self) -> float:
        """Physics-based endurance estimate: minutes remaining."""
        if self.status == "charging":
            return 0.0
        drain_per_min = 1.4  # ~1.4% per minute at cruise
        return max(0.0, (self.battery_pct - 8.0) / drain_per_min)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "latitude": round(self.lat, 6),
            "longitude": round(self.lon, 6),
            "altitude": round(self.altitude, 1),
            "airspeed": round(self.airspeed, 1),
            "heading": round(self.heading, 1),
            "battery_percentage": round(self.battery_pct, 1),
            "battery_voltage": round(self.battery_voltage, 2),
            "current_consumption": round(self.current_amp, 1),
            "battery_temperature": round(self.battery_temp, 1),
            "distance_from_base": round(self.distance_from_base, 1),
            "estimated_flight_time": round(self.estimated_flight_time, 1),
            "home_latitude": self.home_lat,
            "home_longitude": self.home_lon,
            "communication_quality": self.communication_quality,
            "health_score": self.health_score,
            "mission_id": self.mission_id,
            "mission_type": self.mission_type,
            "operational_mode": self.operational_mode,
            "battery_history": self.battery_history[-60:],
            "speed_history": self.speed_history[-60:],
            "altitude_history": self.altitude_history[-60:],
            "cycle_count": self.cycle_count,
        }


@dataclass
class SimAnomaly:
    id: str
    drone_id: str
    object_class: str
    behaviour_type: str
    lat: float
    lon: float
    confidence: float
    risk_score: int
    risk_level: str
    status: str
    sector: str
    description: str
    behaviour_description: str
    risk_breakdown: dict
    detected_at: str
    investigation_drone_id: Optional[str] = None  # properly tracked

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "detected_by_drone_id": self.drone_id,
            "object_class": self.object_class,
            "behaviour_type": self.behaviour_type,
            "latitude": self.lat,
            "longitude": self.lon,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "status": self.status,
            "sector": self.sector,
            "description": self.description,
            "behaviour_description": self.behaviour_description,
            "risk_breakdown": self.risk_breakdown,
            "detected_at": self.detected_at,
            "investigation_drone_id": self.investigation_drone_id,
        }


@dataclass
class SimEvent:
    id: str
    event_type: str
    drone_id: Optional[str]
    title: str
    description: str
    risk_level: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    sector: Optional[str]
    timestamp: str
    anomaly_id: Optional[str] = None
    mission_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "drone_id": self.drone_id,
            "mission_id": self.mission_id,
            "anomaly_id": self.anomaly_id,
            "title": self.title,
            "description": self.description,
            "risk_level": self.risk_level,
            "latitude": self.lat,
            "longitude": self.lon,
            "sector": self.sector,
            "timestamp": self.timestamp,
        }


class SimulationEngine:
    """
    Central simulation engine for PERSIST-AIR.
    - All drones, anomalies, missions and events
    - Physics-based battery drain and movement
    - Predictive handover (general, any drone pair)
    - Dynamic coverage calculation
    - Accelerated simulated time
    - 9 scenario modes
    """

    def __init__(self):
        self.running = False
        self.speed_multiplier = 1
        self.tick = 0
        self.drones: Dict[str, SimDrone] = {}
        self.anomalies: List[SimAnomaly] = []
        self.events: List[SimEvent] = []
        self.missions: List[dict] = []
        self.coverage_percentage = 97.8
        self.coverage_metrics = {"overall": 97.8, "redundant": 70.0, "single": 27.8, "gaps": 0, "status": "STABLE"}
        self.active_handover: Optional[dict] = None
        self.handover_cooldown = 0       # ticks until next handover check
        self.operational_mode = "security"
        self.demo_mode = False
        self.demo_step = 0
        self.demo_tick = 0
        # Simulated mission time (accelerated clock)
        self.sim_start_real = datetime.utcnow()
        self.simulated_seconds = 0       # total simulated seconds elapsed
        self.sim_hours_per_real_hour = 10  # 1 real second = 10 sim seconds
        self._ws_callbacks = []
        self._init_drones()
        self._init_missions()
        self._seed_events()

    # ─── Initialisation ───────────────────────────────────────────────────────

    def _init_drones(self):
        for cfg in DRONE_CONFIGS:
            lat = cfg["route"][0][0] if cfg["route"] else cfg["home_lat"]
            lon = cfg["route"][0][1] if cfg["route"] else cfg["home_lon"]
            d = SimDrone(
                id=cfg["id"],
                name=cfg["name"],
                home_lat=cfg["home_lat"],
                home_lon=cfg["home_lon"],
                lat=lat,
                lon=lon,
                battery_pct=cfg["start_battery"],
                status=cfg["status"],
                route=list(cfg["route"]),
            )
            d.battery_history = [cfg["start_battery"]] * 10
            d.speed_history = [14.0 if cfg["status"] == "active" else 0.0] * 10
            d.altitude_history = [120.0 if cfg["status"] == "active" else 0.0] * 10
            if cfg["status"] in ("charging", "available"):
                d.airspeed = 0.0
                d.altitude = 0.0
                d.lat = cfg["home_lat"]
                d.lon = cfg["home_lon"]
            self.drones[cfg["id"]] = d

        # Assign initial missions
        self.drones["PA-01"].mission_id = "MSN-001"
        self.drones["PA-01"].mission_type = "surveillance"
        self.drones["PA-02"].mission_id = "MSN-002"
        self.drones["PA-02"].mission_type = "patrol"
        self.drones["PA-04"].mission_id = "MSN-003"
        self.drones["PA-04"].mission_type = "surveillance"
        self.drones["PA-05"].mission_id = "MSN-004"
        self.drones["PA-05"].mission_type = "patrol"

    def _init_missions(self):
        self.missions = [
            {
                "id": "MSN-001", "name": "North Sector Patrol", "status": "active",
                "priority": "high", "assigned_drone_id": "PA-01",
                "mission_type": "surveillance", "operational_mode": "security",
                "estimated_duration": 35, "estimated_energy": 28,
                "created_at": "2026-08-17T14:00:00Z", "started_at": "2026-08-17T14:05:00Z",
            },
            {
                "id": "MSN-002", "name": "South Perimeter Watch", "status": "active",
                "priority": "medium", "assigned_drone_id": "PA-02",
                "mission_type": "patrol", "operational_mode": "security",
                "estimated_duration": 25, "estimated_energy": 22,
                "created_at": "2026-08-17T13:45:00Z", "started_at": "2026-08-17T13:50:00Z",
            },
            {
                "id": "MSN-003", "name": "West Boundary Monitor", "status": "active",
                "priority": "high", "assigned_drone_id": "PA-04",
                "mission_type": "surveillance", "operational_mode": "security",
                "estimated_duration": 40, "estimated_energy": 30,
                "created_at": "2026-08-17T14:10:00Z", "started_at": "2026-08-17T14:15:00Z",
            },
            {
                "id": "MSN-004", "name": "East Quadrant Sweep", "status": "active",
                "priority": "low", "assigned_drone_id": "PA-05",
                "mission_type": "patrol", "operational_mode": "security",
                "estimated_duration": 30, "estimated_energy": 24,
                "created_at": "2026-08-17T14:20:00Z", "started_at": "2026-08-17T14:22:00Z",
            },
        ]

    def _seed_events(self):
        seed_events = [
            ("system", None, "PERSIST-AIR System Initialized", "All subsystems nominal. 6 drones online.", None),
            ("detection", "PA-01", "Perimeter scan initiated", "North sector surveillance activated.", "low"),
            ("mission_started", "PA-01", "Mission MSN-001 started", "North Sector Patrol mission commenced.", "low"),
            ("mission_started", "PA-02", "Mission MSN-002 started", "South Perimeter Watch commenced.", "low"),
            ("battery_warning", "PA-02", "Battery warning — PA-02", "Battery below 35%. Endurance limited.", "medium"),
        ]
        base_ts = datetime(2026, 8, 17, 14, 0, 0)
        for i, (etype, drone, title, desc, risk) in enumerate(seed_events):
            self.events.append(SimEvent(
                id=f"EVT-{i:04d}",
                event_type=etype,
                drone_id=drone,
                title=title,
                description=desc,
                risk_level=risk,
                lat=None, lon=None, sector=None,
                timestamp=(base_ts + timedelta(minutes=i * 5)).isoformat() + "Z",
            ))

    # ─── WebSocket ────────────────────────────────────────────────────────────

    def register_ws_callback(self, cb):
        self._ws_callbacks.append(cb)

    def unregister_ws_callback(self, cb):
        try:
            self._ws_callbacks.remove(cb)
        except ValueError:
            pass

    async def _broadcast(self, msg: dict):
        for cb in list(self._ws_callbacks):
            try:
                await cb(msg)
            except Exception:
                pass

    # ─── Event helpers ────────────────────────────────────────────────────────

    def add_event(self, etype: str, drone_id: Optional[str], title: str,
                  description: str, risk_level: Optional[str] = None,
                  lat: Optional[float] = None, lon: Optional[float] = None,
                  sector: Optional[str] = None, anomaly_id: Optional[str] = None,
                  mission_id: Optional[str] = None) -> SimEvent:
        evt = SimEvent(
            id=f"EVT-{uuid.uuid4().hex[:8].upper()}",
            event_type=etype,
            drone_id=drone_id,
            title=title,
            description=description,
            risk_level=risk_level,
            lat=lat, lon=lon, sector=sector,
            timestamp=datetime.utcnow().isoformat() + "Z",
            anomaly_id=anomaly_id,
            mission_id=mission_id,
        )
        self.events.append(evt)
        return evt

    # ─── Movement ─────────────────────────────────────────────────────────────

    def _move_drone_along_route(self, drone: SimDrone, delta_t: float):
        """Move drone one step along its assigned patrol route."""
        if not drone.route or drone.status in ("charging", "available", "offline"):
            return
        target = drone.route[drone.route_idx % len(drone.route)]
        target_lat, target_lon = target
        dlat = target_lat - drone.lat
        dlon = target_lon - drone.lon
        dist = math.sqrt(dlat**2 + dlon**2)
        step = 0.0002 * delta_t * self.speed_multiplier
        if dist < step:
            drone.lat = target_lat
            drone.lon = target_lon
            drone.route_idx = (drone.route_idx + 1) % len(drone.route)
        else:
            drone.lat += (dlat / dist) * step
            drone.lon += (dlon / dist) * step
        if dist > 0:
            drone.heading = (math.degrees(math.atan2(dlon, dlat)) + 360) % 360

    def _move_drone_toward(self, drone: SimDrone, target_lat: float,
                           target_lon: float, delta_t: float) -> bool:
        """Move drone toward an arbitrary target. Returns True when arrived."""
        dlat = target_lat - drone.lat
        dlon = target_lon - drone.lon
        dist = math.sqrt(dlat**2 + dlon**2)
        step = 0.0003 * delta_t * self.speed_multiplier  # slightly faster on direct mission
        if dist < step:
            drone.lat = target_lat
            drone.lon = target_lon
            return True
        drone.lat += (dlat / dist) * step
        drone.lon += (dlon / dist) * step
        if dist > 0:
            drone.heading = (math.degrees(math.atan2(dlon, dlat)) + 360) % 360
        return False

    # ─── Battery ──────────────────────────────────────────────────────────────

    def _update_battery(self, drone: SimDrone, delta_t: float):
        """Physics-based battery drain model."""
        if drone.status == "charging":
            drone.battery_pct = min(100.0, drone.battery_pct + 0.03 * delta_t * self.speed_multiplier)
            if drone.battery_pct >= 95.0:
                drone.status = "available"
                self.add_event("system", drone.id,
                               f"{drone.id} fully charged — available",
                               f"{drone.id} battery at {drone.battery_pct:.0f}%. Ready for deployment.", "low")
            drone.current_amp = 0.0
            return

        if drone.status in ("available", "offline"):
            return

        # Active / returning / investigating
        drain_rate = 0.023 * delta_t * self.speed_multiplier
        if drone.status == "returning":
            drain_rate *= 1.1
        elif drone.status == "investigating":
            drain_rate *= 0.9  # hovering, slightly less drain

        drone.battery_pct = max(0.0, drone.battery_pct - drain_rate)
        drone.battery_voltage = 19.0 + (drone.battery_pct / 100.0) * 3.2
        drone.battery_temp = 28.0 + (100 - drone.battery_pct) * 0.08 + random.uniform(-0.3, 0.3)
        drone.current_amp = 18.5 + random.uniform(-0.5, 0.5)

        # Status transitions
        if drone.battery_pct <= 0.5:
            if drone.status != "offline":
                drone.status = "offline"
                self.add_event("system", drone.id, f"{drone.id} went offline",
                               "Battery depleted. Drone offline.", "critical")
        elif drone.battery_pct <= 12.0 and drone.status not in ("returning", "critical", "charging", "offline"):
            drone.status = "critical"
            self.add_event("battery_critical", drone.id,
                           f"CRITICAL — {drone.id} battery at {drone.battery_pct:.0f}%",
                           f"Drone must return to base immediately.", "critical")
        elif drone.battery_pct <= 22.0 and drone.status not in ("returning", "critical", "charging", "offline", "investigating"):
            drone.status = "returning"
            self._start_return(drone)

    def _start_return(self, drone: SimDrone):
        """Set drone to returning state and log event."""
        drone.status = "returning"
        drone.mission_id = None
        drone.mission_type = None
        self.add_event("battery_warning", drone.id,
                       f"Battery warning — {drone.id} returning to base",
                       f"{drone.id} battery at {drone.battery_pct:.0f}%. Returning to base.", "medium")

    # ─── Returning drones ────────────────────────────────────────────────────

    def _handle_returning(self, drone: SimDrone, delta_t: float):
        """Move returning drone toward home; switch to charging on arrival."""
        if drone.status not in ("returning", "critical"):
            return
        arrived = self._move_drone_toward(drone, drone.home_lat, drone.home_lon, delta_t)
        if arrived:
            drone.status = "charging"
            drone.mission_id = None
            drone.mission_type = None
            drone.route_idx = 0
            self.add_event("system", drone.id,
                           f"{drone.id} returned to base",
                           f"{drone.id} docked and charging.", "low")

    # ─── Investigating drones ────────────────────────────────────────────────

    def _handle_investigating(self, drone: SimDrone, delta_t: float):
        """Move investigating drone toward anomaly target."""
        if drone.status != "investigating":
            return
        if drone.investigation_target_lat is None:
            drone.status = "active"
            return
        arrived = self._move_drone_toward(
            drone, drone.investigation_target_lat,
            drone.investigation_target_lon, delta_t
        )
        if arrived:
            # Mark anomaly as under investigation
            for a in self.anomalies:
                if a.investigation_drone_id == drone.id and a.status == "detected":
                    a.status = "under_investigation"

    # ─── Telemetry noise ─────────────────────────────────────────────────────

    def _update_telemetry_noise(self, drone: SimDrone):
        if drone.status in ("charging", "available", "offline"):
            drone.airspeed = 0.0
            drone.altitude = 0.0
        else:
            drone.airspeed = max(0.0, 14.0 + random.uniform(-1.0, 1.0))
            drone.altitude = max(0.0, 120.0 + random.uniform(-3.0, 3.0))
        # Communication quality degrades slightly with distance and battery
        if drone.status != "offline":
            base_quality = 98 - int(drone.distance_from_base / 200)
            battery_penalty = max(0, int((20 - drone.battery_pct) / 2)) if drone.battery_pct < 20 else 0
            drone.communication_quality = max(60, min(99, base_quality - battery_penalty + random.randint(-1, 1)))

    def _update_history(self, drone: SimDrone):
        drone.battery_history.append(round(drone.battery_pct, 1))
        if len(drone.battery_history) > 120:
            drone.battery_history.pop(0)
        drone.speed_history.append(round(drone.airspeed, 1))
        if len(drone.speed_history) > 120:
            drone.speed_history.pop(0)
        drone.altitude_history.append(round(drone.altitude, 1))
        if len(drone.altitude_history) > 120:
            drone.altitude_history.pop(0)

    # ─── Dynamic Coverage ────────────────────────────────────────────────────

    def _calculate_coverage(self) -> dict:
        """
        Dynamically compute coverage percentage.
        Each active airborne drone covers a circle of COVERAGE_RADIUS_DEG.
        We sample a grid of points over the patrol area and count covered ones.
        """
        active_drones = [
            d for d in self.drones.values()
            if d.status in ("active", "investigating", "patrolling")
        ]
        if not active_drones:
            return {"overall": 0.0, "redundant": 0.0, "single": 0.0, "gaps": 100, "status": "BROKEN"}

        # Patrol area bounds
        lat_min = BASE_LAT - 0.015
        lat_max = BASE_LAT + 0.015
        lon_min = BASE_LON - 0.015
        lon_max = BASE_LON + 0.015

        grid_steps = 25  # 25x25 grid = 625 points
        total = 0
        single_cov = 0
        redundant_cov = 0
        
        for i in range(grid_steps):
            for j in range(grid_steps):
                pt_lat = lat_min + (lat_max - lat_min) * i / grid_steps
                pt_lon = lon_min + (lon_max - lon_min) * j / grid_steps
                total += 1
                
                covering_count = 0
                for drone in active_drones:
                    dlat = drone.lat - pt_lat
                    dlon = drone.lon - pt_lon
                    if math.sqrt(dlat**2 + dlon**2) <= COVERAGE_RADIUS_DEG:
                        covering_count += 1
                
                if covering_count == 1:
                    single_cov += 1
                elif covering_count > 1:
                    redundant_cov += 1

        if total == 0:
            return {"overall": 0.0, "redundant": 0.0, "single": 0.0, "gaps": 0, "status": "BROKEN"}

        noise = math.sin(self.tick / 30) * 0.3
        
        single_pct = max(0.0, (single_cov / total) * 100.0 + noise/2)
        redundant_pct = max(0.0, (redundant_cov / total) * 100.0 + noise/2)
        overall_pct = min(100.0, single_pct + redundant_pct)
        
        if len(active_drones) == 5 and overall_pct > 90:
            status = "STABLE"
        elif len(active_drones) >= 3 and overall_pct > 50:
            status = "DEGRADED"
        else:
            status = "BROKEN"

        return {
            "overall": round(overall_pct, 2),
            "redundant": round(redundant_pct, 2),
            "single": round(single_pct, 2),
            "gaps": total - (single_cov + redundant_cov),
            "status": status
        }

    def get_coverage_zones(self) -> List[dict]:
        """Return per-drone coverage zone info for the map."""
        zones = []
        active = [d for d in self.drones.values()
                  if d.status in ("active", "investigating", "patrolling")]
        for i, drone in enumerate(active):
            zones.append({
                "id": f"ZONE-{drone.id}",
                "lat": drone.lat,
                "lon": drone.lon,
                "radius": int(COVERAGE_RADIUS_DEG * 111000),  # metres
                "drone": drone.id,
                "coverage": round(90.0 + drone.health_score / 10 + random.uniform(-1, 1), 1),
            })
        return zones

    # ─── Handover Engine ─────────────────────────────────────────────────────

    def _find_best_replacement(self, outgoing: SimDrone) -> Optional[SimDrone]:
        """
        Find the best available replacement drone for an outgoing drone's mission.
        Scores on: battery (40%), health (20%), distance from outgoing position (40%).
        """
        candidates = [
            d for d in self.drones.values()
            if d.status in ("available", "charging") and d.id != outgoing.id
            and d.battery_pct >= 50.0  # must have enough to take over
        ]
        if not candidates:
            return None

        def score(d: SimDrone) -> float:
            energy_s = d.battery_pct * 0.40
            health_s = d.health_score * 0.20
            dlat = d.lat - outgoing.lat
            dlon = d.lon - outgoing.lon
            dist_deg = math.sqrt(dlat**2 + dlon**2)
            dist_s = max(0, (1 - dist_deg / 0.05)) * 100 * 0.40
            return energy_s + health_s + dist_s

        return max(candidates, key=score)

    def _check_handover(self):
        """
        General predictive handover check for ALL drones.
        Triggers when any active drone's battery falls below 25% and no handover
        is currently active for that drone.
        """
        if self.handover_cooldown > 0:
            self.handover_cooldown -= 1
            return

        for drone in list(self.drones.values()):
            if drone.status not in ("active", "investigating"):
                continue
            if drone.battery_pct > 25.0:
                continue
            if drone.mission_id is None:
                continue

            # Already in active handover for this drone?
            if (self.active_handover and
                    self.active_handover.get("active_drone") == drone.id and
                    self.active_handover.get("status") != "completed"):
                # Complete handover when battery < 15%
                if drone.battery_pct <= 15.0 and self.active_handover["status"] == "initiated":
                    replacement_id = self.active_handover["replacement_drone"]
                    replacement = self.drones.get(replacement_id)
                    if replacement:
                        replacement.status = "active"
                        replacement.mission_id = drone.mission_id
                        replacement.mission_type = drone.mission_type
                        replacement.route = list(drone.route)
                        replacement.route_idx = drone.route_idx
                        drone.status = "returning"
                        drone.mission_id = None
                        self.active_handover["status"] = "completed"
                        self.add_event(
                            "handover_completed", replacement_id,
                            f"Handover Complete — {replacement_id} assumes patrol",
                            f"{drone.id} returning. {replacement_id} assumed mission.", "low"
                        )
                        self.handover_cooldown = 60
                continue

            # Initiate new handover
            replacement = self._find_best_replacement(drone)
            if not replacement:
                continue

            minutes_to_critical = max(0, (drone.battery_pct - 15) / 1.4)
            self.active_handover = {
                "active_drone": drone.id,
                "replacement_drone": replacement.id,
                "handover_time": datetime.utcnow().isoformat() + "Z",
                "coverage_continuity": round(97.5 + random.uniform(0, 2), 1),
                "confidence": round(92 + random.uniform(0, 5), 1),
                "status": "initiated",
            }
            self.add_event(
                "handover_initiated", drone.id,
                f"Predictive Handover Initiated — {drone.id} → {replacement.id}",
                f"{drone.id} battery at {drone.battery_pct:.0f}%. "
                f"Handover to {replacement.id} predicted in {minutes_to_critical:.0f} min.",
                "medium"
            )

    # ─── Anomaly Generation ───────────────────────────────────────────────────

    def _maybe_generate_anomaly(self):
        """Generate contextual anomalies at realistic intervals."""
        interval = 180  # every 3 real minutes (adjusts with speed)
        if self.tick % max(1, interval // self.speed_multiplier) != 0:
            return

        mode = self.operational_mode
        if mode == "security":
            candidates = [
                ("vehicle", "Circling restricted perimeter", 96.4, 84, "critical",
                 "Vehicle repeatedly circling restricted zone.",
                 "Vehicle remained stationary for 14 minutes inside restricted zone. Expected: Transit through sector.",
                 {"object_classification": 25, "restricted_zone": 20, "behaviour_anomaly": 22, "persistence": 10, "confidence": 7}),
                ("person", "Entering restricted zone", 88.0, 67, "high",
                 "Unauthorized person detected entering restricted zone.",
                 "Person crossed boundary into restricted sector. Baseline: No expected pedestrian traffic.",
                 {"object_classification": 20, "restricted_zone": 18, "behaviour_anomaly": 16, "persistence": 8, "confidence": 5}),
                ("abandoned_object", "Unattended package detected", 79.5, 52, "medium",
                 "Abandoned package detected near entry point.",
                 "Object stationary for 22 minutes. No person observed nearby.",
                 {"object_classification": 15, "restricted_zone": 10, "behaviour_anomaly": 15, "persistence": 8, "confidence": 4}),
                ("group", "Suspicious gathering", 83.0, 61, "high",
                 "Unauthorized group activity detected near perimeter.",
                 "Group of 5+ individuals observed near restricted boundary.",
                 {"object_classification": 20, "restricted_zone": 15, "behaviour_anomaly": 16, "persistence": 7, "confidence": 3}),
            ]
        elif mode == "humanitarian":
            candidates = [
                ("stranded_person", "Person requiring assistance", 91.2, 73, "high",
                 "Stranded person detected in flood-affected region.",
                 "Individual stationary for extended period in hazard zone. Possible distress.",
                 {"object_classification": 22, "hazard_zone": 18, "behaviour_anomaly": 20, "persistence": 8, "confidence": 5}),
                ("fire", "Fire and smoke detected", 95.0, 88, "critical",
                 "Active fire detected with visible smoke plume.",
                 "Thermal signature confirms active combustion spreading east at 2m/s.",
                 {"object_classification": 28, "hazard_zone": 20, "behaviour_anomaly": 22, "persistence": 12, "confidence": 6}),
                ("crowd", "Large crowd in distress area", 87.3, 70, "high",
                 "Dense crowd detected in flood-affected sector.",
                 "Large gathering in evacuation zone — requires immediate assessment.",
                 {"object_classification": 20, "hazard_zone": 16, "behaviour_anomaly": 18, "persistence": 10, "confidence": 6}),
            ]
        else:  # environmental
            candidates = [
                ("deforestation", "Illegal clearing detected", 82.3, 64, "high",
                 "Deforestation activity detected in protected zone.",
                 "Vegetation removal observed vs. baseline imagery. Rate: ~200m² cleared.",
                 {"object_classification": 18, "protected_zone": 16, "behaviour_anomaly": 15, "persistence": 10, "confidence": 5}),
                ("smoke", "Smoke column detected", 90.1, 77, "high",
                 "Smoke column rising from forested area.",
                 "Possible fire origin detected. Wind carrying smoke NE. Not yet confirmed as wildfire.",
                 {"object_classification": 22, "protected_zone": 18, "behaviour_anomaly": 20, "persistence": 10, "confidence": 7}),
                ("water_change", "Water body anomaly", 76.0, 55, "medium",
                 "Significant water boundary change detected.",
                 "Water extent has increased by ~15% compared to 7-day baseline.",
                 {"object_classification": 16, "protected_zone": 12, "behaviour_anomaly": 14, "persistence": 8, "confidence": 5}),
            ]

        c = random.choice(candidates)
        obj_class, beh, conf, risk_score, risk_level, desc, beh_desc, breakdown = c
        patrol_drones = [d for d in self.drones.values() if d.status == "active"]
        if not patrol_drones:
            return
        patrol_drone = random.choice(patrol_drones)
        sector = random.choice(list(SECTOR_MAP.keys()))
        slat, slon = SECTOR_MAP[sector]
        aid = f"ANO-{uuid.uuid4().hex[:6].upper()}"
        anomaly = SimAnomaly(
            id=aid,
            drone_id=patrol_drone.id,
            object_class=obj_class,
            behaviour_type=beh,
            lat=slat + random.uniform(-0.002, 0.002),
            lon=slon + random.uniform(-0.002, 0.002),
            confidence=conf,
            risk_score=risk_score,
            risk_level=risk_level,
            status="detected",
            sector=sector,
            description=desc,
            behaviour_description=beh_desc,
            risk_breakdown=breakdown,
            detected_at=datetime.utcnow().isoformat() + "Z",
        )
        self.anomalies.append(anomaly)

        # Intelligently assign best available drone to investigate
        investigating_drone = self._auto_assign_investigation(anomaly)
        if investigating_drone:
            anomaly.investigation_drone_id = investigating_drone.id
            investigating_drone.status = "investigating"
            investigating_drone.investigation_target_lat = anomaly.lat
            investigating_drone.investigation_target_lon = anomaly.lon
            mid = f"MSN-{uuid.uuid4().hex[:6].upper()}"
            investigating_drone.mission_id = mid
            investigating_drone.mission_type = "investigation"
            self.missions.append({
                "id": mid, "name": f"Investigate {obj_class.replace('_', ' ')} — {sector}",
                "status": "active", "priority": risk_level,
                "assigned_drone_id": investigating_drone.id,
                "mission_type": "investigation",
                "operational_mode": mode,
                "estimated_duration": 15, "estimated_energy": 12,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "started_at": datetime.utcnow().isoformat() + "Z",
                "target_latitude": anomaly.lat, "target_longitude": anomaly.lon,
            })

        self.add_event("detection", patrol_drone.id,
                       f"{patrol_drone.id} detected {obj_class.replace('_', ' ')} — Sector {sector}",
                       desc, risk_level, anomaly.lat, anomaly.lon, sector, aid)
        self.add_event("anomaly", patrol_drone.id,
                       f"Behaviour analysis: {beh}",
                       f"Anomaly score: {risk_score}/100. {beh_desc}", risk_level,
                       anomaly.lat, anomaly.lon, sector, aid)
        self.add_event("risk_assessment", patrol_drone.id,
                       f"Risk Score: {risk_score}/100 — {risk_level.upper()}",
                       f"AI risk assessment complete. Breakdown: {breakdown}",
                       risk_level, anomaly.lat, anomaly.lon, sector, aid)
        self.add_event("verification_requested", patrol_drone.id,
                       "Human verification requested",
                       f"Operator review required for {obj_class.replace('_', ' ')} in Sector {sector}.",
                       risk_level, anomaly.lat, anomaly.lon, sector, aid)
        if investigating_drone:
            self.add_event("drone_selection", investigating_drone.id,
                           f"AI Drone Selection — {investigating_drone.id} dispatched",
                           f"Energy-feasibility check passed. {investigating_drone.id} moving to investigate.",
                           risk_level, anomaly.lat, anomaly.lon, sector, aid)

    def _auto_assign_investigation(self, anomaly: SimAnomaly) -> Optional[SimDrone]:
        """Select best drone to investigate an anomaly using weighted scoring."""
        candidates = [
            d for d in self.drones.values()
            if d.status in ("active", "available") and d.battery_pct > 30
        ]
        if not candidates:
            return None

        def score(d: SimDrone) -> float:
            dlat = d.lat - anomaly.lat
            dlon = d.lon - anomaly.lon
            dist_deg = math.sqrt(dlat**2 + dlon**2)
            energy_s = d.battery_pct * 0.35
            dist_s = max(0, (1 - dist_deg / 0.05)) * 100 * 0.35
            health_s = d.health_score * 0.15
            avail_s = (100 if d.mission_id is None else 60) * 0.15
            return energy_s + dist_s + health_s + avail_s

        return max(candidates, key=score)

    # ─── Simulated Time ───────────────────────────────────────────────────────

    @property
    def simulated_mission_time(self) -> str:
        """Returns HH:MM:SS of accelerated simulated mission time."""
        total_s = int(self.simulated_seconds)
        h = total_s // 3600
        m = (total_s % 3600) // 60
        s = total_s % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    # ─── Scenario System ──────────────────────────────────────────────────────

    def run_scenario(self, scenario: str) -> dict:
        """
        Launch one of 9 predefined scenarios.
        Returns a description of what was triggered.
        """
        scenarios = {
            "normal_patrol": self._scenario_normal_patrol,
            "human_anomaly": self._scenario_human_anomaly,
            "multiple_anomalies": self._scenario_multiple_anomalies,
            "low_battery_handover": self._scenario_low_battery_handover,
            "drone_failure": self._scenario_drone_failure,
            "communication_loss": self._scenario_communication_loss,
            "humanitarian_emergency": self._scenario_humanitarian_emergency,
            "environmental_event": self._scenario_environmental_event,
            "long_duration_persistence": self._scenario_long_duration,
        }
        fn = scenarios.get(scenario)
        if not fn:
            return {"error": f"Unknown scenario: {scenario}"}
        return fn()

    def _scenario_normal_patrol(self) -> dict:
        self.add_event("system", None, "SCENARIO: Normal Patrol",
                       "All drones maintaining standard patrol routes. No active threats.", "low")
        return {"scenario": "normal_patrol", "status": "active"}

    def _scenario_human_anomaly(self) -> dict:
        patrol_drones = [d for d in self.drones.values() if d.status == "active"]
        if not patrol_drones:
            return {"scenario": "human_anomaly", "status": "no_active_drones"}
        drone = patrol_drones[0]
        sector = "B3"
        slat, slon = SECTOR_MAP[sector]
        aid = f"SCEN-{uuid.uuid4().hex[:6].upper()}"
        anomaly = SimAnomaly(
            id=aid, drone_id=drone.id, object_class="person",
            behaviour_type="Entering restricted zone",
            lat=slat + 0.001, lon=slon - 0.001,
            confidence=88.5, risk_score=71, risk_level="high",
            status="detected", sector=sector,
            description="Unauthorized person detected entering restricted zone.",
            behaviour_description="Person crossed restricted boundary at 02:14. No authorised access expected.",
            risk_breakdown={"object_classification": 20, "restricted_zone": 18, "behaviour_anomaly": 20, "persistence": 8, "confidence": 5},
            detected_at=datetime.utcnow().isoformat() + "Z",
        )
        self.anomalies.append(anomaly)
        inv = self._auto_assign_investigation(anomaly)
        if inv:
            anomaly.investigation_drone_id = inv.id
            inv.status = "investigating"
            inv.investigation_target_lat = anomaly.lat
            inv.investigation_target_lon = anomaly.lon
        self.add_event("detection", drone.id, f"SCENARIO: Person anomaly — Sector {sector}",
                       anomaly.description, "high", anomaly.lat, anomaly.lon, sector, aid)
        self.add_event("verification_requested", drone.id,
                       "Operator verification required", "Review detected person activity.", "high",
                       anomaly.lat, anomaly.lon, sector, aid)
        return {"scenario": "human_anomaly", "anomaly_id": aid, "status": "triggered"}

    def _scenario_multiple_anomalies(self) -> dict:
        results = []
        for sector in ["A1", "B4", "C2"]:
            slat, slon = SECTOR_MAP[sector]
            aid = f"SCEN-{uuid.uuid4().hex[:5].upper()}"
            candidates = list(self.drones.values())
            drone = random.choice(candidates) if candidates else None
            if not drone:
                continue
            anomaly = SimAnomaly(
                id=aid, drone_id=drone.id, object_class="vehicle",
                behaviour_type="Simultaneous perimeter breach",
                lat=slat, lon=slon, confidence=85.0, risk_score=78, risk_level="high",
                status="detected", sector=sector,
                description=f"Coordinated vehicle activity in Sector {sector}.",
                behaviour_description="Multiple vehicles approaching from different vectors simultaneously.",
                risk_breakdown={"object_classification": 25, "restricted_zone": 18, "behaviour_anomaly": 20, "persistence": 10, "confidence": 5},
                detected_at=datetime.utcnow().isoformat() + "Z",
            )
            self.anomalies.append(anomaly)
            self.add_event("detection", drone.id, f"SCENARIO: Vehicle — Sector {sector}",
                           anomaly.description, "high", anomaly.lat, anomaly.lon, sector, aid)
            results.append(aid)
        return {"scenario": "multiple_anomalies", "anomaly_ids": results, "count": len(results)}

    def _scenario_low_battery_handover(self) -> dict:
        # Force PA-02's battery to 22% to trigger handover
        drone = self.drones.get("PA-02")
        if drone:
            drone.battery_pct = 22.0
        self.add_event("battery_warning", "PA-02", "SCENARIO: Low-battery handover triggered",
                       "PA-02 battery forced to 22% to demonstrate predictive handover.", "medium")
        return {"scenario": "low_battery_handover", "status": "battery_set_to_22_pct"}

    def _scenario_drone_failure(self) -> dict:
        pa05 = self.drones.get("PA-05")
        if pa05:
            pa05.status = "offline"
            pa05.mission_id = None
            pa05.health_score = 0
            self.add_event("system", "PA-05", "SCENARIO: PA-05 experienced failure",
                           "Drone PA-05 encountered a hardware fault. Status: OFFLINE.", "critical")
        return {"scenario": "drone_failure", "drone": "PA-05", "status": "offline"}

    def _scenario_communication_loss(self) -> dict:
        pa04 = self.drones.get("PA-04")
        if pa04:
            pa04.communication_quality = 8
            self.add_event("system", "PA-04",
                           "SCENARIO: Communication degraded — PA-04",
                           "PA-04 signal quality dropped to 8%. Possible jamming or hardware fault.", "high")
        return {"scenario": "communication_loss", "drone": "PA-04"}

    def _scenario_humanitarian_emergency(self) -> dict:
        old_mode = self.operational_mode
        self.operational_mode = "humanitarian"
        for d in self.drones.values():
            d.operational_mode = "humanitarian"
        aid = f"HUM-{uuid.uuid4().hex[:5].upper()}"
        anomaly = SimAnomaly(
            id=aid, drone_id="PA-01", object_class="stranded_person",
            behaviour_type="Person requiring assistance",
            lat=BASE_LAT - 0.015, lon=BASE_LON + 0.012,
            confidence=92.0, risk_score=80, risk_level="critical",
            status="detected", sector="B3",
            description="Stranded person detected in flooded area. Possible distress signal observed.",
            behaviour_description="Individual stationary for 45+ minutes in flood zone. No movement detected.",
            risk_breakdown={"object_classification": 25, "hazard_zone": 20, "behaviour_anomaly": 22, "persistence": 8, "confidence": 5},
            detected_at=datetime.utcnow().isoformat() + "Z",
        )
        self.anomalies.append(anomaly)
        inv = self._auto_assign_investigation(anomaly)
        if inv:
            anomaly.investigation_drone_id = inv.id
            inv.status = "investigating"
            inv.investigation_target_lat = anomaly.lat
            inv.investigation_target_lon = anomaly.lon
        self.add_event("system", None, "SCENARIO: HUMANITARIAN EMERGENCY",
                       "Mode switched to HUMANITARIAN. Stranded person detected.", "critical",
                       anomaly.lat, anomaly.lon, "B3", aid)
        return {"scenario": "humanitarian_emergency", "anomaly_id": aid, "mode": "humanitarian"}

    def _scenario_environmental_event(self) -> dict:
        self.operational_mode = "environmental"
        for d in self.drones.values():
            d.operational_mode = "environmental"
        aid = f"ENV-{uuid.uuid4().hex[:5].upper()}"
        anomaly = SimAnomaly(
            id=aid, drone_id="PA-04", object_class="smoke",
            behaviour_type="Smoke column — possible wildfire",
            lat=BASE_LAT + 0.018, lon=BASE_LON - 0.014,
            confidence=89.0, risk_score=75, risk_level="high",
            status="detected", sector="C1",
            description="Smoke column detected rising from forested area in Sector C1.",
            behaviour_description="Thermal and visual signature indicates active combustion. Wind NE at ~15 km/h.",
            risk_breakdown={"object_classification": 22, "protected_zone": 18, "behaviour_anomaly": 20, "persistence": 10, "confidence": 5},
            detected_at=datetime.utcnow().isoformat() + "Z",
        )
        self.anomalies.append(anomaly)
        self.add_event("system", None, "SCENARIO: ENVIRONMENTAL EVENT",
                       "Mode switched to ENVIRONMENTAL. Smoke/fire detected.", "high",
                       anomaly.lat, anomaly.lon, "C1", aid)
        return {"scenario": "environmental_event", "anomaly_id": aid}

    def _scenario_long_duration(self) -> dict:
        self.speed_multiplier = 10
        self.sim_hours_per_real_hour = 600  # very fast
        self.add_event("system", None, "SCENARIO: Long-duration persistence simulation",
                       "Speed set to 10x. 1 simulated hour = 6 real minutes. "
                       "Demonstrating 10-hour persistent coverage with drone rotation.", "low")
        return {"scenario": "long_duration_persistence", "speed_multiplier": 10,
                "note": "1 real minute ≈ 10 simulated minutes"}

    # ─── Demo Mode ────────────────────────────────────────────────────────────

    async def _run_demo_step(self):
        """Scripted 11-step SIH demonstration scenario."""
        self.demo_tick += 1
        if self.demo_tick % max(1, 5 * self.speed_multiplier) != 0:
            return

        step = self.demo_step
        pa02 = self.drones.get("PA-02")
        pa04 = self.drones.get("PA-04")

        if step == 0:
            self.add_event("system", None, "LIVE DEMO — PERSIST-AIR Scenario Initiated",
                           "5 drones beginning persistent surveillance mission. Monitoring 6 sectors.", "low")
            self.demo_step += 1

        elif step == 1:
            aid = "DEMO-ANO-001"
            anomaly = SimAnomaly(
                id=aid, drone_id="PA-02",
                object_class="vehicle", behaviour_type="Circling restricted perimeter",
                lat=BASE_LAT - 0.010, lon=BASE_LON + 0.008,
                confidence=96.4, risk_score=82, risk_level="critical",
                status="detected", sector="B4",
                description="Vehicle repeatedly circling restricted zone.",
                behaviour_description="Vehicle remained stationary for 14 minutes inside restricted zone. Expected: Transit through sector.",
                risk_breakdown={"object_classification": 25, "restricted_zone": 20, "behaviour_anomaly": 22, "persistence": 10, "confidence": 7},
                detected_at=datetime.utcnow().isoformat() + "Z",
            )
            if not any(a.id == aid for a in self.anomalies):
                self.anomalies.append(anomaly)
            self.add_event("detection", "PA-02", "PA-02 detected vehicle anomaly — Sector B4",
                           "Unidentified vehicle detected circling restricted perimeter.", "critical",
                           anomaly.lat, anomaly.lon, "B4", aid)
            self.demo_step += 1

        elif step == 2:
            self.add_event("anomaly", "PA-02",
                           "AI Behaviour Analysis — Anomaly confirmed — Risk Score 82/100",
                           "Vehicle circling pattern detected. Isolation Forest anomaly score: 82/100. "
                           "This deviates significantly from baseline traffic patterns.", "critical")
            self.demo_step += 1

        elif step == 3 and pa02:
            self.add_event("feasibility_check", "PA-02",
                           f"Mission feasibility: PA-02 — NOT FEASIBLE",
                           f"PA-02 battery {pa02.battery_pct:.0f}%. Required energy: 31%. "
                           f"Available usable: {max(0, pa02.battery_pct - 8):.0f}%. "
                           "PA-02 cannot safely complete investigation and return.", "high")
            self.demo_step += 1

        elif step == 4 and pa04:
            self.add_event("drone_selection", "PA-04",
                           "AI Drone Selection — PA-04 Recommended (Score: 94/100)",
                           f"PA-04 battery: {pa04.battery_pct:.0f}%. Distance: optimal. "
                           "Energy model predicts sufficient endurance for investigation + return.", "medium")
            self.demo_step += 1

        elif step == 5 and pa04:
            pa04.status = "investigating"
            pa04.mission_id = "DEMO-MSN-001"
            pa04.mission_type = "investigation"
            pa04.investigation_target_lat = BASE_LAT - 0.010
            pa04.investigation_target_lon = BASE_LON + 0.008
            for a in self.anomalies:
                if a.id == "DEMO-ANO-001":
                    a.investigation_drone_id = "PA-04"
            self.add_event("mission_started", "PA-04",
                           "PA-04 dispatched — Energy-aware route generated",
                           "PA-04 moving toward anomaly via optimized energy-aware path. "
                           "ETA: ~3 min. Battery reserve: sufficient.", "medium")
            self.demo_step += 1

        elif step == 6 and pa02:
            self.active_handover = {
                "active_drone": "PA-02",
                "replacement_drone": "PA-04",
                "handover_time": datetime.utcnow().isoformat() + "Z",
                "coverage_continuity": 98.7,
                "confidence": 94.0,
                "status": "initiated",
            }
            self.add_event("handover_initiated", "PA-02",
                           "Predictive Handover Initiated — PA-02 → PA-04",
                           "Coverage continuity: 98.7%. Handover confidence: 94%. "
                           "PA-04 will assume South Perimeter Watch on PA-02 departure.", "medium")
            self.demo_step += 1

        elif step == 7:
            self.add_event("coverage_gap", None,
                           "Coverage maintained above 97%",
                           "Despite ongoing handover, persistent coverage preserved at "
                           f"{self.coverage_percentage:.1f}%. No gaps detected.", "low")
            self.demo_step += 1

        elif step == 8:
            self.add_event("verification_requested", "PA-04",
                           "Human verification requested — DEMO-ANO-001",
                           "Operator review required before mission action. "
                           "AI confidence: 96.4%. Recommend: CONFIRM.", "high")
            self.demo_step += 1

        elif step == 9:
            self.add_event("verification_confirmed", "PA-04",
                           "Human operator confirmed anomaly — CONFIRMED",
                           "Operator: CONFIRMED. PA-04 authorised to investigate and document.", "high")
            for a in self.anomalies:
                if a.id == "DEMO-ANO-001":
                    a.status = "verified"
                    a.investigation_drone_id = "PA-04"
            self.demo_step += 1

        elif step == 10:
            if pa02:
                pa02.status = "returning"
                pa02.mission_id = None
            if self.active_handover:
                self.active_handover["status"] = "completed"
            self.add_event("handover_completed", "PA-04",
                           "Handover Complete — PA-04 assumed patrol, PA-02 returning",
                           "Mission continuity maintained. Coverage uninterrupted.", "low")
            self.demo_step += 1

        elif step == 11:
            self.add_event("mission_completed", "PA-04",
                           "Investigation complete — DEMO-ANO-001 resolved",
                           "PA-04 completed investigation. Event documented. Mission resolved.", "low")
            self.demo_mode = False

    # ─── Main Loop ────────────────────────────────────────────────────────────

    async def tick_loop(self):
        """Main simulation loop — runs every second."""
        while self.running:
            delta_t = 1.0
            self.tick += 1

            # Advance simulated time
            self.simulated_seconds += delta_t * self.sim_hours_per_real_hour / 3600 * 3600
            # (1 real second × speed_mult × sim_hours_per_real_hour hours/hour = simulated seconds)
            self.simulated_seconds += delta_t * (self.sim_hours_per_real_hour - 1) * self.speed_multiplier

            for drone in list(self.drones.values()):
                if drone.status in ("returning", "critical"):
                    self._handle_returning(drone, delta_t)
                elif drone.status == "investigating":
                    self._handle_investigating(drone, delta_t)
                else:
                    self._move_drone_along_route(drone, delta_t)
                self._update_battery(drone, delta_t)
                self._update_telemetry_noise(drone)
                if self.tick % 5 == 0:
                    self._update_history(drone)

            # Dynamic coverage
            if self.tick % max(1, 10 // self.speed_multiplier) == 0:
                self.coverage_metrics = self._calculate_coverage()
                self.coverage_percentage = self.coverage_metrics["overall"]

            # Handover check
            self._check_handover()

            # Anomaly generation
            self._maybe_generate_anomaly()

            # Demo mode
            if self.demo_mode:
                await self._run_demo_step()

            # Broadcast telemetry
            payload = {
                "type": "telemetry",
                "drones": [d.to_dict() for d in self.drones.values()],
                "anomalies": [a.to_dict() for a in self.anomalies[-20:]],
                "events": [e.to_dict() for e in self.events[-50:]],
                "coverage_percentage": round(self.coverage_percentage, 2),
                "coverage_metrics": self.coverage_metrics,
                "active_handover": self.active_handover,
                "tick": self.tick,
                "simulated_mission_time": self.simulated_mission_time,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            await self._broadcast(payload)

            sleep_time = 1.0 / max(1, self.speed_multiplier)
            await asyncio.sleep(sleep_time)

    # ─── Control ──────────────────────────────────────────────────────────────

    def start(self):
        self.running = True

    def pause(self):
        self.running = False

    def reset(self):
        self.running = False
        self.tick = 0
        self.demo_step = 0
        self.demo_tick = 0
        self.demo_mode = False
        self.active_handover = None
        self.handover_cooldown = 0
        self.anomalies = []
        self.events = []
        self.drones = {}
        self.missions = []
        self.simulated_seconds = 0
        self.coverage_percentage = 97.8
        self._init_drones()
        self._init_missions()
        self._seed_events()

    def set_speed(self, multiplier: int):
        self.speed_multiplier = max(1, min(10, multiplier))

    def start_demo(self):
        self.demo_mode = True
        self.demo_step = 0
        self.demo_tick = 0
        self.running = True


# Singleton
simulation = SimulationEngine()
