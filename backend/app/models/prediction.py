from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, index
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.database import Base

class FloodPrediction(Base):
    __tablename__ = "flood_predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_time = Column(DateTime(timezone=True), nullable = False, index=True)
    valid_time = Column(DateTime(timezone=True), nullable = False)

    #Risk assessment
    risk_level = Column(String(20))
    risk_score = Column(Float)
    confidence = Column(Float)
    
    #Spatial data
    risk_area = Column(Geometry('POLYGON', srid=4326))
    affected_gauges = Column(JSON)

    #rainfall forecast
    rainfall_forecast_in = Column(Float)
    soil_saturation_pct = Column(Float)
    upstream_flow_cfs = Column(Float)

    #Metadata
    model_version = Column(String(20))
    processing_time_ms = Column(Float)
    created_at = Column(DateTime(timezone=True), nullable = False, server_default=func.now())

    __table_args = (
        Index('idx_prediction_time', 'prediction_time'),
        Index('idx_prediction_risk', 'risk_level', 'predicition_time'),
        Index('idx_prediction_area', 'risk_area', postgresql_using='gist')
    )

class RIskZone(Base):
    __tablename__ = "risk_zones"

    id = Column(Integer, primary_key=True, index=True)
    zone_name = COlumn(String(100), nullable=False)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=False)
    base_risk_level = Column(String(20))
    population_estimation = Column(Integer)
    critical_infrastructure = Column(JSON)
    elevation_avg_ft = Column(Float)
    elevation_min_ft = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_zone_geometry', 'geometry', postgresql_using='gist'),
    )