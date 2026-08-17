# PERSIST-AIR REST API Reference

> Version 1.0.0 | Base URL: `http://localhost:8000`

All responses are JSON. All timestamps are ISO 8601 UTC.

---

## Authentication

No authentication required for local development.  
For production, add `Authorization: Bearer <token>` header.

---

## Drones

### GET /api/drones

Returns telemetry for all drones in the fleet.

**Response:**
```json
[
  {
    "id": "PA-01",
    "name": "PERSIST ALPHA-01",
    "status": "active",
    "latitude": 28.6248,
    "longitude": 77.2014,
    "altitude": 120.4,
    "airspeed": 14.2,
    "heading": 45.0,
    "battery_percentage": 78.3,
    "battery_voltage": 21.71,
    "current_consumption": 18.6,
    "battery_temperature": 29.4,
    "distance_from_base": 1423.5,
    "estimated_flight_time": 50.2,
    "communication_quality": 97,
    "health_score": 100,
    "mission_id": "MSN-001",
    "mission_type": "surveillance",
    "operational_mode": "security",
    "battery_history": [...],
    "speed_history": [...],
    "altitude_history": [...],
    "cycle_count": 45
  }
]
```

Drone `status` values: `active`, `investigating`, `returning`, `charging`, `available`, `offline`, `critical`

---

### GET /api/drones/{id}

Returns telemetry for a single drone.

---

## Fleet

### GET /api/fleet/status

Comprehensive fleet summary.

**Response:**
```json
{
  "total_drones": 6,
  "by_status": {"active": ["PA-01", "PA-04"], "charging": ["PA-03"]},
  "average_battery": 72.4,
  "average_health": 98.0,
  "coverage_percentage": 97.4,
  "active_handover": false,
  "drones": [...]
}
```

---

## Missions

### GET /api/missions

Returns all missions.

### GET /api/missions/{id}

Returns a single mission.

### POST /api/missions

Create a new mission.

**Request:**
```json
{
  "name": "North Sector Investigation",
  "priority": "high",
  "assigned_drone_id": "PA-04",
  "mission_type": "investigation",
  "operational_mode": "security"
}
```

---

## Anomalies

### GET /api/anomalies

Returns all detected anomalies.

**Response:**
```json
[
  {
    "id": "ANO-ABC123",
    "detected_by_drone_id": "PA-02",
    "investigation_drone_id": "PA-04",
    "object_class": "vehicle",
    "behaviour_type": "Circling restricted perimeter",
    "latitude": 28.614,
    "longitude": 77.215,
    "confidence": 0.964,
    "risk_score": 82,
    "risk_level": "critical",
    "status": "detected",
    "sector": "B4",
    "description": "Vehicle repeatedly circling restricted zone.",
    "behaviour_description": "...",
    "risk_breakdown": {"object_classification": 25, "restricted_zone": 20, ...},
    "detected_at": "2026-08-17T14:22:00Z"
  }
]
```

Anomaly `status` values: `detected`, `under_investigation`, `verified`, `dismissed`

---

### GET /api/anomalies/{id}

Single anomaly detail.

### POST /api/anomalies/{id}/verify

Human verification action.

**Request:**
```json
{"action": "confirm"}
```
or
```json
{"action": "dismiss"}
```

---

## Intelligence Events

### GET /api/events

Returns last 100 events, newest first.

**Response:**
```json
[
  {
    "id": "EVT-A1B2C3D4",
    "event_type": "detection",
    "drone_id": "PA-02",
    "anomaly_id": "ANO-ABC123",
    "title": "PA-02 detected vehicle — Sector B4",
    "description": "Unidentified vehicle detected circling perimeter.",
    "risk_level": "critical",
    "latitude": 28.614,
    "longitude": 77.215,
    "sector": "B4",
    "timestamp": "2026-08-17T14:22:05Z"
  }
]
```

Event types: `system`, `detection`, `anomaly`, `risk_assessment`, `verification_requested`, `verification_confirmed`, `verification_dismissed`, `mission_started`, `mission_completed`, `battery_warning`, `battery_critical`, `handover_initiated`, `handover_completed`, `coverage_gap`, `drone_selection`, `feasibility_check`

---

## Coverage

### GET /api/coverage

Dynamic coverage data calculated from live drone positions.

**Response:**
```json
{
  "coverage_percentage": 97.42,
  "uncovered_percentage": 2.58,
  "predicted_continuity": 98.3,
  "active_drones": 4,
  "zones": [
    {
      "id": "ZONE-PA-01",
      "lat": 28.624,
      "lon": 77.201,
      "radius": 777,
      "drone": "PA-01",
      "coverage": 95.4
    }
  ],
  "active_handover": null
}
```

---

## AI & ML Endpoints

### POST /api/ai/detect

Object detection inference.

**Request:**
```json
{
  "frame_id": "frame-001",
  "drone_id": "PA-01",
  "operational_mode": "security"
}
```

**Response:**
```json
{
  "detections": [...],
  "frame_id": "frame-001",
  "processing_time_ms": 45.2,
  "model_source": "SIMULATION"
}
```

`model_source`: `REAL_MODEL (Synthetic Training Data)` | `SIMULATION` | `PRETRAINED_YOLOV8N_COCO`

---

### POST /api/ai/behaviour

Behaviour anomaly analysis.

**Request:** See `BehaviourInput` schema in `backend/app/ml/base.py`

---

### POST /api/ai/risk

Risk scoring.

**Request:** See `RiskInput` schema in `backend/app/ml/base.py`

---

## Energy & Battery

### POST /api/energy/predict

Endurance prediction for a drone.

**Request:**
```json
{
  "drone_id": "PA-02",
  "battery_percentage": 29.0,
  "battery_voltage": 19.93,
  "current_consumption": 18.5,
  "temperature": 30.0,
  "airspeed": 14.0,
  "altitude": 120.0,
  "distance_from_base": 1200.0,
  "wind_factor": 1.0,
  "payload_weight": 0.0
}
```

**Response:**
```json
{
  "remaining_endurance_minutes": 14.3,
  "safe_mission_time": 5.4,
  "return_reserve_minutes": 8.9,
  "energy_risk": "high",
  "confidence": 0.922,
  "predicted_battery_curve": [{"t": 0, "pct": 29.0}, ...],
  "model_source": "REAL_MODEL (Synthetic Training Data)"
}
```

---

### POST /api/battery/health

Battery State of Health prediction.

**Request:**
```json
{
  "drone_id": "PA-02",
  "cycle_count": 85,
  "average_temperature": 28.0,
  "depth_of_discharge": 80.0,
  "current_capacity_mah": 5200.0,
  "nominal_capacity_mah": 5200.0,
  "voltage_sag": 0.3
}
```

**Response:**
```json
{
  "state_of_health": 96.6,
  "estimated_remaining_capacity_mah": 5023.0,
  "estimated_remaining_cycles": 90,
  "degradation_rate": 0.0412,
  "recommendation": "HEALTHY",
  "confidence": 0.913,
  "model_source": "REAL_MODEL (Synthetic Training Data)"
}
```

`recommendation` values: `HEALTHY`, `MONITOR`, `REPLACE_SOON`, `REPLACE`

---

### POST /api/mission/feasibility

Check if a drone has enough energy for a mission.

**Request:**
```json
{
  "drone_id": "PA-02",
  "battery_percentage": 29.0,
  "distance_to_target_m": 1500.0,
  "estimated_investigation_minutes": 10.0,
  "return_distance_m": 1200.0,
  "wind_factor": 1.1,
  "mission_priority": "high"
}
```

**Response:**
```json
{
  "result": "NOT_FEASIBLE",
  "estimated_mission_energy": 35.2,
  "available_usable_energy": 21.0,
  "required_return_reserve": 8.0,
  "predicted_completion_time": "14:35:00",
  "confidence": 0.921,
  "recommendation": "Insufficient energy. Assign a drone with higher battery..."
}
```

`result` values: `FEASIBLE`, `MARGINAL`, `NOT_FEASIBLE`

---

### POST /api/mission/select-drone

AI drone selection with weighted scoring.

**Request:**
```json
{"target_lat": 28.614, "target_lon": 77.215}
```

**Response:**
```json
{
  "candidates": [
    {
      "drone_id": "PA-04",
      "score": 91.2,
      "battery_percentage": 87.0,
      "feasible": true,
      "reasons": ["sufficient energy reserve", "close proximity", "mission feasibility check: PASSED"]
    }
  ],
  "recommended": {"drone_id": "PA-04", ...}
}
```

---

### POST /api/path/plan

Energy-aware path planning.

### POST /api/handover/predict

Handover timing prediction for a drone.

---

## Simulation Control

### GET /api/simulation/state

Full simulation state including simulated mission time.

### POST /api/simulation/start | /pause | /reset | /speed | /demo

Control simulation playback.

### POST /api/simulation/mode

Switch operational mode.

**Request:** `{"mode": "humanitarian"}` — values: `security`, `humanitarian`, `environmental`

### POST /api/simulation/scenario

Run a named scenario.

**Request:**
```json
{"scenario": "human_anomaly"}
```

Available scenarios: `normal_patrol`, `human_anomaly`, `multiple_anomalies`, `low_battery_handover`, `drone_failure`, `communication_loss`, `humanitarian_emergency`, `environmental_event`, `long_duration_persistence`

---

## System

### GET /api/system/status

System health check with operational summary.

---

## WebSocket

### WS /ws/telemetry

Real-time telemetry broadcast (every second).

**Message format:**
```json
{
  "type": "telemetry",
  "drones": [...],
  "anomalies": [...],
  "events": [...],
  "coverage_percentage": 97.42,
  "active_handover": null,
  "simulated_mission_time": "01:23:45",
  "tick": 1234,
  "timestamp": "2026-08-17T14:23:45Z"
}
```

**Client ping** (keep-alive):
```json
{"type": "ping"}
```
