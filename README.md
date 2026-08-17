# PERSIST-AIR — AI-Powered Persistent Aerial Intelligence and Energy Management System

> **"PERSIST-AIR does not make one drone fly forever. It makes the MISSION persistent."**

PERSIST-AIR is a production-quality aerospace command-and-control (C2) web application built for multi-drone aerial intelligence, energy management, predictive handovers, and behavioural anomaly detection.

---

## Key Features

1. **Energy Intelligence & Endurance Prediction**: Physics-based & ML-ready battery degradation forecasting and return reserve calculation.
2. **Mission Feasibility Engine**: Evaluates whether active drones can safely investigate anomalies prior to dispatch.
3. **Intelligent Drone Allocation Matrix**: Multi-criteria decision engine scoring fleet assets based on energy, distance, workload, and signal strength.
4. **Energy-Aware Path Planning**: Compares geometric shortest paths against wind/altitude optimized low-energy flight trajectories.
5. **Predictive Drone Handover**: Proactively initiates mid-air drone handovers to prevent coverage gaps before battery depletion.
6. **Persistent Coverage Intelligence**: Real-time sector coverage monitoring demonstrating continuous 10+ hour mission endurance.
7. **AI Behavioural Anomaly Detection**: Temporal pattern recognition identifying loitering, circling, intrusion, and unusual movements.
8. **Explainable Risk Scoring Model**: Transparent 0–100 risk scoring breakdown (Object class, Sector sensitivity, Temporal persistence, Confidence).
9. **Human-in-the-Loop Verification**: Operator approval workflow for high-consequence surveillance actions.
10. **Digital Twin Simulation**: Multi-drone scenario playback with speed controls (1x, 5x, 10x) and side-by-side gap comparison.
11. **Operational Modes**: Dynamic switching between Security, Humanitarian, and Environmental mission presets.

---

## System Architecture

```
[ Frontend: React + TS + Tailwind + Leaflet ]
                  │
                  ▼ (REST & WebSockets)
[ Backend: Python FastAPI + Simulation Engine ]
                  │
                  ▼ (Adapter Pattern)
[ ML Service Interface: Replaceable AI Models ]
```

---

## Quick Start (Local Development)

### Prerequisites
- Node.js (v18+)
- Python (v3.11+)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Backend API will be live at `http://localhost:8000` (Interactive Swagger docs at `http://localhost:8000/docs`).

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Frontend application will be live at `http://localhost:5173`.

---

## Running with Docker Compose

Deploy the complete stack in a single command:

```bash
docker-compose up --build
```
- Web Application: `http://localhost`
- Backend API: `http://localhost:8000`

---

## Connecting Real ML Models

The system is designed with a strict ML adapter abstraction layer in `backend/app/ml/`.
To connect a trained model:
1. Update `backend/app/ml/factory.py` to point your custom implementation (e.g. YOLOv8, RT-DETR, or PyTorch models).
2. Set `ML_SERVICE_URL` in `.env` if hosting ML inference on an external GPU microservice.
3. The frontend and API contracts remain completely unchanged.

---

## Hackathon Pitch / Live Demo Scenario

Click the **LIVE DEMO** button in the top navigation bar to trigger a 17-step scripted mission scenario:
1. Surveillance scan starts across 4 active drones.
2. PA-02 detects a vehicle anomaly in Sector B4.
3. AI scores behavioural risk at 82/100 (CRITICAL).
4. Feasibility engine determines PA-02 has insufficient energy for deep investigation.
5. AI selection engine scores PA-04 as the optimal replacement asset.
6. Energy-aware route generated for PA-04.
7. Predictive handover initiated between PA-02 and PA-04 while keeping coverage >97%.
8. Operator confirms anomaly via Human-in-the-Loop modal.
9. Event logged into the Intelligence Timeline.
