"""
Historical flood data models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base


class HistoricalFlood(Base):
    """Historical flood events"""
    __tablename__ = "historical_floods"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(200), nullable=False)
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Location information
    location_name = Column(String(200))
    geometry = Column(Geometry('POLYGON', srid=4326))

    # Gauge information
    gauge_id = Column(Integer, ForeignKey('river_gauges.id'), nullable=True)
    peak_gauge_height_ft = Column(Float)
    peak_flow_cfs = Column(Float)

    # Impact assessment
    severity = Column(String(20))  # minor, moderate, major, catastrophic
    affected_area_sqmi = Column(Float)
    estimated_damage_usd = Column(Float)
    casualties = Column(Integer, default=0)
    evacuations = Column(Integer, default=0)

    # Meteorological data
    total_precipitation_in = Column(Float)
    duration_hours = Column(Float)
    return_period_years = Column(Integer)  # e.g., 100-year flood

    # Description and notes
    description = Column(Text)
    cause = Column(String(200))  # rainfall, snowmelt, dam_failure, etc.
    sources = Column(JSON)  # List of data sources/references

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    verified = Column(Boolean, default=False)
    verified_by = Column(String(100))

    # Relationships
    impacts = relationship("FloodImpact", back_populates="flood_event", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_historical_date', 'event_date'),
        Index('idx_historical_severity', 'severity'),
        Index('idx_historical_geometry', 'geometry', postgresql_using='gist'),
    )


class FloodEvent(Base):
    """Detailed flood event timeline"""
    __tablename__ = "flood_events"

    id = Column(Integer, primary_key=True, index=True)
    historical_flood_id = Column(Integer, ForeignKey('historical_floods.id'))

    # Timeline information
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    event_type = Column(String(50))  # warning_issued, peak_reached, evacuation_started, etc.

    # Event details
    description = Column(Text)
    gauge_height_ft = Column(Float)
    flow_cfs = Column(Float)
    water_level_change_rate = Column(Float)  # ft/hr

    # Location
    location = Column(Geometry('POINT', srid=4326))
    location_name = Column(String(200))

    # Additional data
    meta_data = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_event_timestamp', 'event_timestamp'),
        Index('idx_event_flood', 'historical_flood_id'),
    )


class FloodImpact(Base):
    """Detailed impact assessment for flood events"""
    __tablename__ = "flood_impacts"

    id = Column(Integer, primary_key=True, index=True)
    historical_flood_id = Column(Integer, ForeignKey('historical_floods.id'), nullable=False)

    # Impact category
    category = Column(String(50), nullable=False)  # infrastructure, residential, commercial, agricultural, environmental
    subcategory = Column(String(100))

    # Location
    location_name = Column(String(200))
    geometry = Column(Geometry('POINT', srid=4326))
    address = Column(String(300))

    # Impact details
    description = Column(Text)
    severity = Column(String(20))  # minor, moderate, severe, destroyed

    # Quantitative measures
    affected_units = Column(Integer)  # e.g., number of buildings
    estimated_damage_usd = Column(Float)
    recovery_time_days = Column(Integer)

    # Infrastructure specific
    infrastructure_type = Column(String(100))  # road, bridge, water_system, power_grid, etc.
    service_disruption_hours = Column(Float)

    # Environmental impact
    contamination_type = Column(String(100))
    wildlife_affected = Column(Boolean, default=False)

    # Additional data
    photos = Column(JSON)  # URLs to photos
    documents = Column(JSON)  # URLs to related documents
    meta_data = Column(JSON)

    # Metadata
    reported_by = Column(String(100))
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    flood_event = relationship("HistoricalFlood", back_populates="impacts")

    __table_args__ = (
        Index('idx_impact_category', 'category'),
        Index('idx_impact_flood', 'historical_flood_id'),
        Index('idx_impact_geometry', 'geometry', postgresql_using='gist'),
    )


class FloodRecurrence(Base):
    """Flood recurrence intervals and statistics"""
    __tablename__ = "flood_recurrence"

    id = Column(Integer, primary_key=True, index=True)
    gauge_id = Column(Integer, ForeignKey('river_gauges.id'), nullable=False)

    # Recurrence interval (e.g., 2-year, 10-year, 100-year flood)
    return_period_years = Column(Integer, nullable=False)

    # Statistical values
    discharge_cfs = Column(Float)
    gauge_height_ft = Column(Float)

    # Probability
    annual_exceedance_probability = Column(Float)  # 1/return_period

    # Calculation method
    method = Column(String(100))  # log_pearson_type_3, gumbel, etc.
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)

    # Data used for calculation
    years_of_record = Column(Integer)
    calculation_date = Column(DateTime(timezone=True))
    data_source = Column(String(200))

    # Metadata
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_recurrence_gauge', 'gauge_id', 'return_period_years'),
    )


class FloodDamageFunction(Base):
    """Depth-damage functions for flood impact estimation"""
    __tablename__ = "flood_damage_functions"

    id = Column(Integer, primary_key=True, index=True)

    # Building/structure type
    structure_type = Column(String(100), nullable=False)  # residential_1story, commercial, etc.
    occupancy_type = Column(String(100))

    # Depth-damage relationship
    depth_ft = Column(Float, nullable=False)
    damage_percent = Column(Float, nullable=False)  # Percentage of structure value

    # Regional adjustments
    region = Column(String(100))
    foundation_type = Column(String(50))  # basement, slab, crawlspace

    # Metadata
    source = Column(String(200))
    version = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_damage_func_type', 'structure_type', 'depth_ft'),
    )