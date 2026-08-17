# PERSIST-AIR

## AI-Powered Persistent Aerial Intelligence and Energy Management

A complete multi-drone intelligent surveillance and energy management platform for Smart India Hackathon (SIH).

**The core innovation:** PERSIST-AIR solves the fundamental UAV endurance problem — individual drones are limited to ~35 minutes of battery life. Through AI-driven predictive handovers and fleet orchestration, PERSIST-AIR delivers **10+ hours of continuous coverage** from a single platform.

---

## System Architecture

```
PERSIST-AIR
├── frontend/          React + TypeScript + Vite (port 5173)
├── backend/           FastAPI + Python (port 8000)
├── ml_service/        ML inference service (port 8001)
├── scripts/           Dataset generation, training, demo
├── models/            Trained model files
├── data/              Datasets (generated, not committed)
├── reports/           Evaluation reports
└── docs/              API and integration documentation
```

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **pip** (Python package manager)

---

## Quick Start (3 Terminals)

### Terminal 1 — Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — ML Service (optional)

```bash
cd ml_service
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8001
```

### Terminal 3 — Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

---

## Environment Setup

```bash
cp .env.example backend/.env
# Edit backend/.env if needed
```

The default `.env` uses SQLite and simulation mode — no database configuration required.

---

## Training ML Models (Optional)

The system runs with simulation-based models by default. To train real scikit-learn models:

```bash
# Step 1: Generate synthetic datasets
python scripts/generate_energy_dataset.py
python scripts/generate_anomaly_dataset.py
python scripts/generate_battery_dataset.py

# Step 2: Train all models
python scripts/train_energy_model.py
python scripts/train_anomaly_model.py
python scripts/train_battery_model.py

# Step 3: Restart backend — it auto-detects and loads trained models
```

> ⚠️ **All models are trained on SYNTHETIC data** (physics-inspired, not real UAV flight data). All outputs are labeled accordingly.

---

## SIH Demo

```bash
# 1. Start backend (Terminal 1)
cd backend && python -m uvicorn app.main:app --reload --port 8000

# 2. Start frontend (Terminal 2)
cd frontend && npm run dev

# 3. Run demo (Terminal 3)
python scripts/run_demo.py
```

The demo triggers the complete 11-step scripted scenario:
1. Fleet initialized (6 drones, 6 sectors)
2. Anomaly detected (vehicle circling restricted zone)
3. AI behaviour analysis (Isolation Forest score: 82/100)
4. Mission feasibility check (PA-02: NOT FEASIBLE — insufficient energy)
5. AI drone selection (PA-04: score 94/100)
6. PA-04 dispatched with energy-aware route
7. Predictive handover initiated (PA-02 → PA-04)
8. Coverage maintained >97% throughout handover
9. Human verification requested
10. Operator confirms — PA-04 authorised
11. Mission resolved, PA-02 returns, coverage maintained

---

## Complete Workflow

```
CAMERA/SENSOR
      ↓
OBJECT DETECTION (YOLOv8n or simulation)
      ↓
OBJECT TRACKING (track_id, trajectory)
      ↓
BEHAVIOURAL ANALYSIS (Isolation Forest)
      ↓
ANOMALY SCORE (0-100)
      ↓
RISK SCORE (weighted multi-factor)
      ↓
EVENT CREATED
      ↓
MISSION FEASIBILITY (energy budget check)
      ↓
BEST DRONE SELECTED (weighted scoring)
      ↓
ENERGY-AWARE ROUTE
      ↓
MISSION ASSIGNED
      ↓
DRONE MOVES IN SIMULATION
      ↓
BATTERY/TELEMETRY UPDATES (real-time WebSocket)
      ↓
HANDOVER PREDICTION (continuous monitoring)
      ↓
REPLACEMENT DRONE ASSIGNED
      ↓
ORIGINAL DRONE RETURNS
      ↓
EVENT VERIFIED (human-in-the-loop)
      ↓
MISSION RESOLVED
      ↓
PERSISTENT COVERAGE MAINTAINED
```

---

## Operational Modes

| Mode | Use Case |
|------|----------|
| **SECURITY** | Perimeter surveillance, restricted zone monitoring |
| **HUMANITARIAN** | Disaster response, search & rescue |
| **ENVIRONMENTAL** | Wildfire detection, deforestation monitoring |

Switch mode via Settings page or API: `POST /api/simulation/mode`

---

## Simulation Scenarios

| Scenario | Description |
|----------|-------------|
| `normal_patrol` | Standard fleet patrol |
| `human_anomaly` | Person entering restricted zone |
| `multiple_anomalies` | Coordinated threat simulation |
| `low_battery_handover` | Force PA-02 low battery → handover |
| `drone_failure` | PA-05 hardware failure simulation |
| `communication_loss` | PA-04 signal degradation |
| `humanitarian_emergency` | Stranded person in flood zone |
| `environmental_event` | Wildfire smoke detection |
| `long_duration_persistence` | 10x speed: 10-hour mission demonstration |

Trigger via: `POST /api/simulation/scenario {"scenario": "human_anomaly"}`

---

## API Reference

See `docs/API.md` for complete endpoint documentation.

Quick reference:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/drones` | All drone telemetry |
| GET | `/api/fleet/status` | Fleet summary |
| GET | `/api/missions` | Active missions |
| GET | `/api/anomalies` | Detected anomalies |
| GET | `/api/events` | Intelligence timeline |
| GET | `/api/coverage` | Live coverage data |
| GET | `/api/simulation/state` | Simulation state |
| POST | `/api/energy/predict` | Endurance prediction |
| POST | `/api/battery/health` | Battery SoH prediction |
| POST | `/api/mission/feasibility` | Mission energy check |
| POST | `/api/mission/select-drone` | AI drone selection |
| POST | `/api/path/plan` | Energy-aware route |
| POST | `/api/handover/predict` | Handover timing |
| POST | `/api/simulation/demo` | Start demo scenario |
| POST | `/api/simulation/scenario` | Run named scenario |
| WS | `/ws/telemetry` | Real-time telemetry |

---

## Real-Time WebSocket

Connect to `ws://localhost:8000/ws/telemetry`

Broadcasts every second:
```json
{
  "type": "telemetry",
  "drones": [...],
  "anomalies": [...],
  "events": [...],
  "coverage_percentage": 97.4,
  "active_handover": null,
  "simulated_mission_time": "01:23:45",
  "tick": 1234
}
```

---

## ML Models

| Model | Algorithm | Data | Label |
|-------|-----------|------|-------|
| Energy Endurance | Random Forest / XGBoost | Synthetic physics | SYNTHETIC-BASED |
| Behaviour Anomaly | Isolation Forest | Synthetic behaviour | SYNTHETIC-BASED |
| Battery Health | Random Forest | Synthetic LiPo degradation | SYNTHETIC-BASED |
| Object Detection | YOLOv8n (COCO) | COCO dataset | PRETRAINED |

> **Important:** Fire/smoke detection with YOLO requires custom fine-tuning on a fire/smoke dataset (not included). Without it, the system uses domain-aware simulation for these classes.

---

## Responsible Operation

PERSIST-AIR is a **decision-support system**. Critical decisions remain human-controlled:
- All anomalies require human verification before action
- The system recommends; operators decide
- No autonomous targeting or harmful actions

Designed for: security surveillance research, disaster response, environmental monitoring.

---

## Docker (Full Stack)

```bash
cp .env.example .env
# Set SECRET_KEY in .env
docker-compose up --build
```

Services:
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- ML Service: http://localhost:8001

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| WebSocket disconnects | Check backend is running on port 8000 |
| No drones on map | Verify WebSocket connected (check TopBar indicator) |
| ML models not loading | Run training scripts; check `models/` directory |
| CORS error | Ensure `CORS_ORIGINS` includes your frontend URL |
| Port conflict | Change ports in `.env` and `vite.config.ts` |
| `asyncio` error | Use Python 3.11+ (asyncio is stdlib, not pip) |

---

## Project Structure Detail

```
backend/app/
├── api/
│   ├── drones.py      GET /api/drones, /api/drones/{id}
│   ├── missions.py    GET/POST /api/missions
│   ├── anomalies.py   GET/POST /api/anomalies (verify)
│   ├── ai.py          POST /api/ai/detect, /behaviour, /risk
│   ├── energy.py      POST /api/energy/predict, /battery/health, /mission/*
│   └── system.py      GET/POST /api/simulation/*, /events, /coverage
├── ml/
│   ├── base.py        Abstract interfaces for all ML models
│   ├── mocks.py       Simulation implementations (labeled SIMULATION)
│   ├── real_energy.py Real RF/XGBoost endurance model
│   ├── real_anomaly.py Real Isolation Forest anomaly model
│   ├── real_battery.py Real RF battery health model
│   └── factory.py     Auto-load real models, fallback to mocks
└── simulation/
    └── engine.py      Full 6-drone simulation engine
```
