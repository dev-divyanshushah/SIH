"""
PERSIST-AIR Backend — FastAPI Application
==========================================
AI-Powered Persistent Aerial Intelligence and Energy Management System
"""
import asyncio
import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import (
    drones_router, missions_router, anomalies_router,
    ai_router, energy_router, system_router,
)
from app.websocket.manager import manager
from app.simulation.engine import simulation

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("persist-air")

app = FastAPI(
    title="PERSIST-AIR API",
    description="AI-Powered Persistent Aerial Intelligence and Energy Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(drones_router)
app.include_router(missions_router)
app.include_router(anomalies_router)
app.include_router(ai_router)
app.include_router(energy_router)
app.include_router(system_router)

# ─── WebSocket ───────────────────────────────────────────────────────────────
@app.websocket("/ws/telemetry")
async def telemetry_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info(f"WS client connected: {websocket.client}")
    try:
        # Register broadcast callback
        async def ws_callback(data: dict):
            await manager.broadcast(data)

        simulation.register_ws_callback(ws_callback)

        # Send initial state immediately
        initial = {
            "type": "telemetry",
            "drones": [d.to_dict() for d in simulation.drones.values()],
            "anomalies": [a.to_dict() for a in simulation.anomalies[-20:]],
            "events": [e.to_dict() for e in simulation.events[-50:]],
            "coverage_percentage": simulation.coverage_percentage,
            "active_handover": simulation.active_handover,
            "tick": simulation.tick,
        }
        await websocket.send_text(json.dumps(initial))

        # Keep alive — listen for client messages (ping/pong or mode changes)
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                # Send keep-alive
                await websocket.send_text(json.dumps({"type": "keepalive"}))
    except WebSocketDisconnect:
        logger.info("WS client disconnected")
    except Exception as e:
        logger.error(f"WS error: {e}")
    finally:
        manager.disconnect(websocket)
        try:
            simulation.unregister_ws_callback(ws_callback)
        except Exception:
            pass


# ─── Lifecycle ────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("PERSIST-AIR backend starting...")
    simulation.start()
    asyncio.create_task(simulation.tick_loop())
    logger.info("Simulation engine started ✓")


@app.on_event("shutdown")
async def shutdown():
    simulation.pause()
    logger.info("PERSIST-AIR backend shutting down.")


@app.get("/")
async def root():
    return {
        "system": "PERSIST-AIR",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
    }
