from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime

class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(String, primary_key=True)
    drone_id = Column(String, ForeignKey("drones.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    airspeed = Column(Float)
    heading = Column(Float)
    battery_percentage = Column(Float)
    battery_voltage = Column(Float)
    current_consumption = Column(Float)
    battery_temperature = Column(Float)
    distance_from_base = Column(Float)
    estimated_flight_time = Column(Float)
    communication_quality = Column(Float)

    drone = relationship("Drone", back_populates="telemetry_records")
