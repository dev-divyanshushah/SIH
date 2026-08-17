from sqlalchemy import Column, String, Float, DateTime, Enum as SAEnum, Integer
from app.database.base import Base
from datetime import datetime
import enum

class EventType(str, enum.Enum):
    DETECTION = "detection"
    ANOMALY = "anomaly"
    RISK_ASSESSMENT = "risk_assessment"
    FEASIBILITY_CHECK = "feasibility_check"
    DRONE_SELECTION = "drone_selection"
    HANDOVER_INITIATED = "handover_initiated"
    HANDOVER_COMPLETED = "handover_completed"
    VERIFICATION_REQUESTED = "verification_requested"
    VERIFICATION_CONFIRMED = "verification_confirmed"
    VERIFICATION_DISMISSED = "verification_dismissed"
    MISSION_STARTED = "mission_started"
    MISSION_COMPLETED = "mission_completed"
    BATTERY_WARNING = "battery_warning"
    BATTERY_CRITICAL = "battery_critical"
    COVERAGE_GAP = "coverage_gap"
    SYSTEM = "system"

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    event_type = Column(SAEnum(EventType), nullable=False)
    drone_id = Column(String, nullable=True)
    mission_id = Column(String, nullable=True)
    anomaly_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    sector = Column(String, nullable=True)
    metadata_json = Column(String, nullable=True)  # JSON string for extra data
    timestamp = Column(DateTime, default=datetime.utcnow)
