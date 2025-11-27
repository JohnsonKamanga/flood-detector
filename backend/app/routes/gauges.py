from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, timedelta
from geoalchemy2.functions import ST_DWithin, ST_MakePoint

from app.database import get_db
from app.models.gauge import RiverGauge, GaugeMeasurement
from app.services.usgs_service import USGSService
from pydantic import BaseModel

router = APIRouter()

# Response models
class GaugeResponse(BaseModel):
    id: int
    usgs_site_id: str
    name: str
    latitude: float
    longitude: float
    current_flow_cfs: Optional[float]
    current_gauge_height_ft: Optional[float]
    current_stage: Optional[str]
    last_updated: datetime

    class Config:
        from_attributes = True

class MeasurementResponse(BaseModel):
    id: int
    timestamp: datetime
    flow_cfs: Optional[float]
    gauge_height_ft: Optional[float]
    precipitation_in: Optional[float]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[GaugeResponse])
async def get_gauges(
    lat: Optional[float] = Query(None, description="Latitude for proximity search"),
    lon: Optional[float] = Query(None, description="Longitude for proximity search"),
    radius_km: float = Query(50, description="Search radius in kilometers"),
    stage: Optional[str] = Query(None, description="Filter by current stage"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of river gauges, optionally filtered by location or stage"""

    query = select(RiverGauge).where(RiverGauge.is_active == True)

    # Filter by proximity if coordinates provided
    if lat is not None and lon is not None:
        # Convert km to meters for ST_DWithin
        radius_meters = radius_km * 1000
        point = ST_MakePoint(lon, lat)
        query = query.where(
            ST_DWithin(RiverGauge.location, point, radius_meters)
        )

    # Filter by stage
    if stage:
        query = query.where(RiverGauge.current_stage == stage)

    result = await db.execute(query)
    gauges = result.scalars().all()

    return gauges

@router.get("/{gauge_id}", response_model=GaugeResponse)
async def get_gauge(
    gauge_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific gauge details"""

    result = await db.execute(
        select(RiverGauge).where(RiverGauge.id == gauge_id)
    )
    gauge = result.scalar_one_or_none()

    if not gauge:
        raise HTTPException(status_code=404, detail="Gauge not found")

    return gauge

@router.get("/{gauge_id}/measurements", response_model=List[MeasurementResponse])
async def get_gauge_measurements(
    gauge_id: int,
    hours: int = Query(24, description="Number of hours of historical data"),
    db: AsyncSession = Depends(get_db)
):
    """Get historical measurements for a gauge"""

    # Verify gauge exists
    gauge_result = await db.execute(
        select(RiverGauge).where(RiverGauge.id == gauge_id)
    )
    if not gauge_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Gauge not found")

    # Get measurements
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    result = await db.execute(
        select(GaugeMeasurement)
        .where(
            and_(
                GaugeMeasurement.gauge_id == gauge_id,
                GaugeMeasurement.timestamp >= cutoff_time
            )
        )
        .order_by(GaugeMeasurement.timestamp.desc())
    )

    measurements = result.scalars().all()

    return measurements

@router.post("/refresh/{usgs_site_id}")
async def refresh_gauge_data(
    usgs_site_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Manually refresh data for a specific gauge"""

    # Find gauge
    result = await db.execute(
        select(RiverGauge).where(RiverGauge.usgs_site_id == usgs_site_id)
    )
    gauge = result.scalar_one_or_none()

    if not gauge:
        raise HTTPException(status_code=404, detail="Gauge not found")

    # Fetch fresh data from USGS
    async with USGSService() as usgs:
        try:
            data = await usgs.get_site_data([usgs_site_id])

            if usgs_site_id in data:
                site_data = data[usgs_site_id]
                measurements = site_data.get('measurements', [])

                if measurements:
                    # Update gauge with latest measurement
                    latest = measurements[0]

                    if latest['parameter'] == '00060':  # Discharge
                        gauge.current_flow_cfs = latest['value']
                    elif latest['parameter'] == '00065':  # Gauge height
                        gauge.current_gauge_height_ft = latest['value']

                    gauge.last_updated = datetime.utcnow()

                    await db.commit()

                    return {
                        "status": "success",
                        "message": f"Updated gauge {usgs_site_id}",
                        "timestamp": gauge.last_updated
                    }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching USGS data: {str(e)}"
            )

    raise HTTPException(status_code=500, detail="No data available")