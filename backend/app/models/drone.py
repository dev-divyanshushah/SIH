from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime
import enum

class DroneStatus(str, enum.Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    RETURNING = "returning"
    CHARGING = "charging"
    CRITICAL = "critical"
    OFFLINE = "offline"

class Drone(Base):
    __tablename__ = "drones"

    id = Column(String, primary_key=True)  # PA-01, PA-02...
    name = Column(String, nullable=False)
    model = Column(String, default="DJI Matrice 300 RTK")
    status = Column(SAEnum(DroneStatus), default=DroneStatus.AVAILABLE)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, default=0.0)
    airspeed = Column(Float, default=0.0)
    heading = Column(Float, default=0.0)
    battery_percentage = Column(Float, default=100.0)
    battery_voltage = Column(Float, default=22.2)
    current_consumption = Column(Float, default=0.0)
    battery_temperature = Column(Float, default=25.0)
    distance_from_base = Column(Float, default=0.0)
    estimated_flight_time = Column(Float, default=35.0)
    home_latitude = Column(Float, nullable=False)
    home_longitude = Column(Float, nullable=False)
    communication_quality = Column(Integer, default=100)  # 0-100
    health_score = Column(Integer, default=100)  # 0-100
    current_mission_id = Column(String, nullable=True)
    operational_mode = Column(String, default="security")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    telemetry_records = relationship("Telemetry", back_populates="drone", lazy="dynamic")
