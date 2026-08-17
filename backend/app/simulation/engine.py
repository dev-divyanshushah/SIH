"""
PERSIST-AIR Simulation Engine
Simulates realistic drone behavior:
- Gradual battery depletion (not random jumps)
- Route-following movement
- Anomaly event generation
- Drone handover logic
- Coverage maintenance
"""
import asyncio
import math
import random
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict

# ─── Drone base routes (waypoints near New Delhi, India) ────────────────────
BASE_LAT = 28.6139
BASE_LON = 77.2090

DRONE_CONFIGS = [
    {
        "id": "PA-01",
        "name": "PERSIST ALPHA-01",
        "home_lat": BASE_LAT + 0.002,
        "home_lon": BASE_LON - 0.003,
        "start_battery": 94.0,
        "route": [
            (BASE_LAT + 0.010, BASE_LON - 0.008),
            (BASE_LAT + 0.015, BASE_LON + 0.002),
            (BASE_LAT + 0.008, BASE_LON + 0.012),
            (BASE_LAT + 0.002, BASE_LON + 0.005),
        ],
        "status": "active",
    },
    {
        "id": "PA-02",
        "name": "PERSIST ALPHA-02",
        "home_lat": BASE_LAT - 0.002,
        "home_lon": BASE_LON + 0.003,
        "start_battery": 29.0,
        "route": [
            (BASE_LAT - 0.008, BASE_LON + 0.010),
            (BASE_LAT - 0.014, BASE_LON + 0.005),
            (BASE_LAT - 0.010, BASE_LON - 0.005),
            (BASE_LAT - 0.004, BASE_LON - 0.008),
        ],
        "status": "active",
    },
    {
        "id": "PA-03",
        "name": "PERSIST ALPHA-03",
        "home_lat": BASE_LAT + 0.001,
        "home_lon": BASE_LON + 0.004,
        "start_battery": 100.0,
        "route": [],
        "status": "charging",
    },
    {
        "id": "PA-04",
        "name": "PERSIST ALPHA-04",
        "home_lat": BASE_LAT - 0.001,
        "home_lon": BASE_LON - 0.004,
        "start_battery": 87.0,
        "route": [
            (BASE_LAT + 0.005, BASE_LON - 0.015),
            (BASE_LAT + 0.012, BASE_LON - 0.010),
            (BASE_LAT + 0.018, BASE_LON - 0.002),
            (BASE_LAT + 0.010, BASE_LON + 0.008),
        ],
        "status": "active",
    },
    {
        "id": "PA-05",
        "name": "PERSIST ALPHA-05",
        "home_lat": BASE_LAT + 0.003,
        "home_lon": BASE_LON + 0.001,
        "start_battery": 68.0,
        "route": [
            (BASE_LAT - 0.012, BASE_LON - 0.012),
            (BASE_LAT - 0.018, BASE_LON - 0.005),
            (BASE_LAT - 0.015, BASE_LON + 0.008),
        ],
        "status": "active",
    },
    {
        "id": "PA-06",
        "name": "PERSIST ALPHA-06",
        "home_lat": BASE_LAT - 0.003,
        "home_lon": BASE_LON - 0.001,
        "start_battery": 100.0,
        "route": [],
        "status": "available",
    },
]

SECTOR_MAP = {
    "A1": (BASE_LAT + 0.010, BASE_LON - 0.008),
    "A2": (BASE_LAT + 0.015, BASE_LON + 0.002),
    "B3": (BASE_LAT - 0.008, BASE_LON + 0.010),
    "B4": (BASE_LAT - 0.014, BASE_LON + 0.005),
    "C1": (BASE_LAT + 0.005, BASE_LON - 0.015),
    "C2": (BASE_LAT + 0.012, BASE_LON - 0.010),
}


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
    route: List = field(default_factory=list)
    route_idx: int = 0
    communication_quality: int = 98
    health_score: int = 100
    operational_mode: str = "security"
    # battery history for charts (last 60 readings)
    battery_history: List[float] = field(default_factory=list)
    speed_history: List[float] = field(default_factory=list)
    altitude_history: List[float] = field(default_factory=list)

    @property
    def distance_from_base(self) -> float:
        dlat = self.lat - self.home_lat
        dlon = self.lon - self.home_lon
        return math.sqrt(dlat**2 + dlon**2) * 111000  # rough meters

    @property
    def estimated_flight_time(self) -> float:
        """Rough minutes remaining based on current battery and drain rate."""
        if self.status == "charging":
            return 0.0
        drain_per_min = 1.4  # ~1.4% per minute at cruise
        return max(0.0, (self.battery_pct - 8.0) / drain_per_min)  # 8% return reserve

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
            "investigation_drone_id": None,
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
    Maintains state for all drones, anomalies, missions and events.
    Runs an async loop that updates every second.
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
        self.active_handover: Optional[dict] = None
        self.operational_mode = "security"
        self.demo_mode = False
        self.demo_step = 0
        self.demo_tick = 0
        self._ws_callbacks = []
        self._init_drones()
        self._init_missions()
        self._seed_events()

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
            if cfg["status"] == "charging":
                d.airspeed = 0.0
                d.altitude = 0.0
                d.lat = cfg["home_lat"]
                d.lon = cfg["home_lon"]
            self.drones[cfg["id"]] = d

        # Assign missions
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
        from datetime import timedelta
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

    def register_ws_callback(self, cb):
        self._ws_callbacks.append(cb)

    def unregister_ws_callback(self, cb):
        self._ws_callbacks.remove(cb)

    async def _broadcast(self, msg: dict):
        for cb in list(self._ws_callbacks):
            try:
                await cb(msg)
            except Exception:
                pass

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

    def _move_drone_along_route(self, drone: SimDrone, delta_t: float):
        """Move drone one step along its route."""
        if not drone.route or drone.status in ("charging", "available", "offline"):
            return
        target = drone.route[drone.route_idx % len(drone.route)]
        target_lat, target_lon = target
        dlat = target_lat - drone.lat
        dlon = target_lon - drone.lon
        dist = math.sqrt(dlat**2 + dlon**2)
        step = 0.00004 * delta_t * self.speed_multiplier  # degrees per second
        if dist < step:
            drone.lat = target_lat
            drone.lon = target_lon
            drone.route_idx = (drone.route_idx + 1) % len(drone.route)
        else:
            drone.lat += (dlat / dist) * step
            drone.lon += (dlon / dist) * step
        # Update heading
        if dist > 0:
            drone.heading = (math.degrees(math.atan2(dlon, dlat)) + 360) % 360

    def _update_battery(self, drone: SimDrone, delta_t: float):
        """Realistic battery drain based on status."""
        if drone.status == "charging":
            # Charge at ~0.5% per second (slow realistic charge)
            drone.battery_pct = min(100.0, drone.battery_pct + 0.03 * delta_t * self.speed_multiplier)
            if drone.battery_pct >= 95.0:
                drone.status = "available"
            drone.current_amp = 0.0
            return

        if drone.status in ("available", "offline"):
            return

        # Active / returning — drain battery
        drain_rate = 0.023 * delta_t * self.speed_multiplier  # ~1.4% per minute
        if drone.status == "returning":
            drain_rate *= 1.1  # slightly higher during return

        drone.battery_pct = max(0.0, drone.battery_pct - drain_rate)
        drone.battery_voltage = 19.0 + (drone.battery_pct / 100.0) * 3.2
        drone.battery_temp = 28.0 + (100 - drone.battery_pct) * 0.08 + random.uniform(-0.3, 0.3)
        drone.current_amp = 18.5 + random.uniform(-0.5, 0.5)

        # Status transitions
        if drone.battery_pct <= 0.5:
            drone.status = "offline"
        elif drone.battery_pct <= 12.0 and drone.status not in ("returning", "critical"):
            drone.status = "critical"
        elif drone.battery_pct <= 22.0 and drone.status not in ("returning", "critical"):
            drone.status = "returning"

    def _update_telemetry_noise(self, drone: SimDrone):
        """Add subtle noise to altitude and speed for realism."""
        if drone.status in ("charging", "available", "offline"):
            drone.airspeed = 0.0
            drone.altitude = 0.0
        else:
            drone.airspeed = max(0.0, 14.0 + random.uniform(-1.0, 1.0))
            drone.altitude = max(0.0, 120.0 + random.uniform(-3.0, 3.0))

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

    def _check_handover(self):
        """Check if PA-02 needs handover to PA-04."""
        pa02 = self.drones.get("PA-02")
        pa04 = self.drones.get("PA-04")
        if not pa02 or not pa04:
            return
        if pa02.battery_pct <= 20.0 and self.active_handover is None and pa02.status != "charging":
            self.active_handover = {
                "active_drone": "PA-02",
                "replacement_drone": "PA-04",
                "handover_time": datetime.utcnow().isoformat() + "Z",
                "coverage_continuity": 98.7,
                "confidence": 94.0,
                "status": "initiated",
            }
            self.add_event(
                "handover_initiated", "PA-02",
                "Predictive Handover Initiated — PA-02 → PA-04",
                f"PA-02 battery at {pa02.battery_pct:.0f}%. Handover to PA-04 predicted in 06:42.",
                "medium",
            )
        if self.active_handover and pa02.battery_pct <= 12.0 and self.active_handover["status"] == "initiated":
            self.active_handover["status"] = "completed"
            pa04.mission_id = pa02.mission_id
            pa02.status = "returning"
            self.add_event(
                "handover_completed", "PA-04",
                "Handover Complete — PA-04 assumes patrol",
                "PA-02 returning to base. PA-04 has assumed South Perimeter Watch.",
                "low",
            )

    def _maybe_generate_anomaly(self):
        """Periodically generate realistic anomalies."""
        if self.tick % 180 != 0:  # every 3 minutes
            return
        mode = self.operational_mode
        if mode == "security":
            candidates = [
                ("vehicle", "Circling restricted perimeter", 96.4, 84, "critical",
                 "Vehicle repeatedly circling restricted zone.",
                 "Vehicle remained stationary for 14 minutes inside restricted zone.",
                 {"object_classification": 25, "restricted_zone": 20, "behaviour_anomaly": 22, "persistence": 10, "confidence": 7}),
                ("person", "Entering restricted zone", 88.0, 67, "high",
                 "Unauthorized person detected entering restricted zone.",
                 "Person crossed boundary into restricted sector.",
                 {"object_classification": 20, "restricted_zone": 18, "behaviour_anomaly": 16, "persistence": 8, "confidence": 5}),
                ("abandoned_object", "Unattended package", 79.5, 52, "medium",
                 "Abandoned package detected near entry point.",
                 "Object stationary for 22 minutes.",
                 {"object_classification": 15, "restricted_zone": 10, "behaviour_anomaly": 15, "persistence": 8, "confidence": 4}),
            ]
        elif mode == "humanitarian":
            candidates = [
                ("stranded_person", "Person requiring assistance", 91.2, 73, "high",
                 "Stranded person detected in flooded region.",
                 "Individual stationary for extended period in flood zone.",
                 {"object_classification": 22, "hazard_zone": 18, "behaviour_anomaly": 20, "persistence": 8, "confidence": 5}),
                ("fire", "Fire/smoke detected", 95.0, 88, "critical",
                 "Active fire detected with smoke plume.",
                 "Thermal signature confirms active fire, spreading east.",
                 {"object_classification": 28, "hazard_zone": 20, "behaviour_anomaly": 22, "persistence": 12, "confidence": 6}),
            ]
        else:
            candidates = [
                ("deforestation", "Illegal clearing detected", 82.3, 64, "high",
                 "Deforestation activity detected in protected zone.",
                 "Vegetation removal observed compared to baseline imagery.",
                 {"object_classification": 18, "protected_zone": 16, "behaviour_anomaly": 15, "persistence": 10, "confidence": 5}),
            ]

        c = random.choice(candidates)
        obj_class, beh, conf, risk_score, risk_level, desc, beh_desc, breakdown = c
        patrol_drone = random.choice(["PA-01", "PA-04", "PA-05"])
        sector = random.choice(list(SECTOR_MAP.keys()))
        slat, slon = SECTOR_MAP[sector]
        aid = f"ANO-{uuid.uuid4().hex[:6].upper()}"
        anomaly = SimAnomaly(
            id=aid,
            drone_id=patrol_drone,
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
        self.add_event(
            "detection", patrol_drone,
            f"{patrol_drone} detected {obj_class.replace('_', ' ')} — Sector {sector}",
            desc,
            risk_level,
            anomaly.lat, anomaly.lon, sector, aid,
        )
        self.add_event(
            "risk_assessment", patrol_drone,
            f"Risk Score: {risk_score}/100 — {risk_level.upper()}",
            f"Anomaly score: {risk_score}. Breakdown: {breakdown}",
            risk_level,
            anomaly.lat, anomaly.lon, sector, aid,
        )
        self.add_event(
            "verification_requested", patrol_drone,
            "Human verification requested",
            f"Operator review required for {obj_class.replace('_', ' ')} in Sector {sector}.",
            risk_level,
            anomaly.lat, anomaly.lon, sector, aid,
        )

    async def tick_loop(self):
        """Main simulation loop — runs every second."""
        while self.running:
            delta_t = 1.0
            self.tick += 1

            for drone in self.drones.values():
                self._move_drone_along_route(drone, delta_t)
                self._update_battery(drone, delta_t)
                self._update_telemetry_noise(drone)
                # Update history every 5 ticks
                if self.tick % 5 == 0:
                    self._update_history(drone)

            # Coverage fluctuates slightly
            self.coverage_percentage = 97.8 + math.sin(self.tick / 60) * 0.5

            # Check handover
            self._check_handover()

            # Maybe generate anomaly
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
                "active_handover": self.active_handover,
                "tick": self.tick,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            await self._broadcast(payload)

            sleep_time = 1.0 / self.speed_multiplier
            await asyncio.sleep(sleep_time)

    async def _run_demo_step(self):
        """Scripted 17-step demo scenario."""
        self.demo_tick += 1
        if self.demo_tick % (5 * self.speed_multiplier) != 0:
            return

        step = self.demo_step
        pa02 = self.drones.get("PA-02")
        pa04 = self.drones.get("PA-04")

        if step == 0:
            self.add_event("system", None, "LIVE DEMO — Scenario Initiated",
                           "4 drones beginning persistent surveillance mission.", "low")
            self.demo_step += 1
        elif step == 1 and pa02:
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
            self.anomalies.append(anomaly)
            self.add_event("detection", "PA-02",
                           "PA-02 detected vehicle anomaly — Sector B4",
                           "Unidentified vehicle detected circling restricted perimeter.", "critical",
                           anomaly.lat, anomaly.lon, "B4", aid)
            self.demo_step += 1
        elif step == 2:
            self.add_event("anomaly", "PA-02",
                           "Behaviour anomaly confirmed — Risk Score 82/100",
                           "AI behaviour analysis: vehicle circling pattern detected. Anomaly score: 82/100.", "critical")
            self.demo_step += 1
        elif step == 3 and pa02:
            self.add_event("feasibility_check", "PA-02",
                           f"Mission feasibility: PA-02 — NOT FEASIBLE",
                           f"PA-02 battery {pa02.battery_pct:.0f}%. Required energy: 31%. Available usable: 24%. PA-02 cannot safely complete investigation.", "high")
            self.demo_step += 1
        elif step == 4:
            self.add_event("drone_selection", "PA-04",
                           "AI Drone Selection — PA-04 Recommended",
                           "PA-04 scores 94/100. Sufficient energy reserve. Lowest predicted mission completion time.", "medium")
            self.demo_step += 1
        elif step == 5 and pa04:
            pa04.mission_id = "DEMO-MSN-001"
            pa04.mission_type = "investigation"
            self.add_event("mission_started", "PA-04",
                           "PA-04 dispatched — Energy-aware route generated",
                           "PA-04 moving toward ANOMALY-DEMO-001 via optimized energy-aware path.", "medium")
            self.demo_step += 1
        elif step == 6 and pa02:
            pa02.status = "returning"
            self.add_event("handover_initiated", "PA-02",
                           "Predictive handover initiated — PA-02 → PA-04",
                           "Coverage continuity: 98.7%. Handover confidence: 94%.", "medium")
            self.demo_step += 1
        elif step == 7:
            self.add_event("system", None,
                           "Coverage maintained above 95%",
                           "Despite handover, persistent coverage preserved at 97.8%.", "low")
            self.demo_step += 1
        elif step == 8:
            self.add_event("verification_requested", "PA-04",
                           "Human verification requested — ANOMALY-DEMO-001",
                           "Operator review required before mission action.", "high")
            self.demo_step += 1
        elif step == 9:
            self.add_event("verification_confirmed", "PA-04",
                           "Human operator confirmed anomaly",
                           "Operator: CONFIRMED. PA-04 authorised to investigate.", "high")
            # Mark anomaly verified
            for a in self.anomalies:
                if a.id == "DEMO-ANO-001":
                    a.status = "verified"
                    a.investigation_drone_id = "PA-04"
            self.demo_step += 1
        elif step == 10:
            self.add_event("mission_completed", "PA-04",
                           "Investigation complete — ANOMALY-DEMO-001 resolved",
                           "PA-04 completed investigation. Event logged to intelligence timeline.", "low")
            self.demo_mode = False  # Demo done
            self.demo_step += 1

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
        self.anomalies = []
        self.events = []
        self.drones = {}
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
