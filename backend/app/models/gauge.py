from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.database import Base

class RiverGauge(Base):
    __tablename__ = "river_gauges"

    id = Column(Integer, primary_key=True, index=True)
    usgs_site_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_ft = Column(Float)
    drainage_area_sqmi = Column(Float)

    # current status
    current_flow_cfs = Column(Float)
    current_guage_height_ft = Column(Float)
    current_stage = Column(String(20))
    last_updated = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Thresholds
    action_stage_ft = Column(Float)
    flood_stage_ft = Column(Float)
    major_flood_stage_ft = Column(Float)
    
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    

class GaugeMeasurement(Base):
    __tablename__ = "gauge_measurements"

    id = Column(Integer, primary_key=True, index=True)
    gauge_id = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    flow_cfs = Column(Float)
    gauge_height_ft = Column(Float)
    precipitation_in = Column(Float)
    temperature_f = Column(Float)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    