from sqlalchemy import Column, String, Float, DateTime, Enum as SAEnum, Boolean, Integer
from app.database.base import Base
from datetime import datetime
import enum

class MissionStatus(str, enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABORTED = "aborted"
    PENDING_HANDOVER = "pending_handover"

class MissionPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Mission(Base):
    __tablename__ = "missions"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(SAEnum(MissionStatus), default=MissionStatus.PLANNED)
    priority = Column(SAEnum(MissionPriority), default=MissionPriority.MEDIUM)
    assigned_drone_id = Column(String, nullable=True)
    target_latitude = Column(Float, nullable=True)
    target_longitude = Column(Float, nullable=True)
    mission_type = Column(String, default="surveillance")  # surveillance, investigation, patrol
    operational_mode = Column(String, default="security")
    estimated_duration = Column(Float, default=30.0)  # minutes
    estimated_energy = Column(Float, default=25.0)  # battery %
    route_waypoints = Column(String, nullable=True)  # JSON string
    coverage_zone_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
