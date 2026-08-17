from sqlalchemy import Column, String, Float, DateTime, Enum as SAEnum, Integer, Boolean
from app.database.base import Base
from datetime import datetime
import enum

class AnomalyRisk(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AnomalyStatus(str, enum.Enum):
    DETECTED = "detected"
    UNDER_INVESTIGATION = "under_investigation"
    VERIFIED = "verified"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(String, primary_key=True)
    detected_by_drone_id = Column(String, nullable=False)
    object_class = Column(String, nullable=False)  # vehicle, person, fire, etc.
    behaviour_type = Column(String, nullable=True)  # circling, stationary, intruding
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1
    risk_score = Column(Integer, nullable=False)  # 0-100
    risk_level = Column(SAEnum(AnomalyRisk), default=AnomalyRisk.MEDIUM)
    status = Column(SAEnum(AnomalyStatus), default=AnomalyStatus.DETECTED)
    sector = Column(String, nullable=True)
    description = Column(String, nullable=True)
    behaviour_description = Column(String, nullable=True)
    risk_breakdown = Column(String, nullable=True)  # JSON
    verification_operator = Column(String, nullable=True)
    investigation_drone_id = Column(String, nullable=True)
    operational_mode = Column(String, default="security")
    detected_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
