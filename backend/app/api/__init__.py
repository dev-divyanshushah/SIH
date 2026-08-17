from app.api.drones import router as drones_router
from app.api.missions import router as missions_router
from app.api.anomalies import router as anomalies_router
from app.api.ai import router as ai_router
from app.api.energy import router as energy_router
from app.api.system import router as system_router

__all__ = [
    "drones_router", "missions_router", "anomalies_router",
    "ai_router", "energy_router", "system_router",
]
