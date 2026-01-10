"""
API routes for historical flood data
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.historical_service import HistoricalFloodService
from app.utils.exceptions import ResourceNotFoundError, DataValidationError, DatabaseError

router = APIRouter()


# Pydantic models
class FloodImpactCreate(BaseModel):
    category: str = Field(..., description="Impact category")
    subcategory: Optional[str] = None
    location_name: Optional[str] = None
    description: Optional[str] = None
    severity: str = Field(..., description="Impact severity")
    affected_units: Optional[int] = None
    estimated_damage_usd: Optional[float] = None


class FloodImpactResponse(BaseModel):
    id: int
    historical_flood_id: int
    category: str
    severity: str
    description: Optional[str]
    estimated_damage_usd: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class HistoricalFloodCreate(BaseModel):
    event_name: str = Field(..., max_length=200)
    event_date: datetime
    location_name: Optional[str] = None
    gauge_id: Optional[int] = None
    peak_gauge_height_ft: Optional[float] = None
    peak_flow_cfs: Optional[float] = None
    severity: str = Field(..., description="minor, moderate, major, catastrophic")
    affected_area_sqmi: Optional[float] = None
    estimated_damage_usd: Optional[float] = None
    casualties: Optional[int] = 0
    evacuations: Optional[int] = 0
    total_precipitation_in: Optional[float] = None
    duration_hours: Optional[float] = None
    return_period_years: Optional[int] = None
    description: Optional[str] = None
    cause: Optional[str] = None


class HistoricalFloodUpdate(BaseModel):
    event_name: Optional[str] = None
    severity: Optional[str] = None
    estimated_damage_usd: Optional[float] = None
    description: Optional[str] = None
    verified: Optional[bool] = None
    verified_by: Optional[str] = None


class HistoricalFloodResponse(BaseModel):
    id: int
    event_name: str
    event_date: datetime
    location_name: Optional[str]
    severity: str
    peak_gauge_height_ft: Optional[float]
    peak_flow_cfs: Optional[float]
    estimated_damage_usd: Optional[float]
    casualties: int
    evacuations: int
    description: Optional[str]
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FloodStatisticsResponse(BaseModel):
    total_events: int
    by_severity: dict
    total_damage_usd: float
    total_casualties: int
    total_evacuations: int
    average_damage_per_event: float


class RecurrenceIntervalResponse(BaseModel):
    id: int
    return_period_years: int
    discharge_cfs: Optional[float]
    gauge_height_ft: Optional[float]
    annual_exceedance_probability: Optional[float]

    class Config:
        from_attributes = True


# Routes

@router.get("", response_model=List[HistoricalFloodResponse])
async def get_historical_floods(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: AsyncSession = Depends(get_db)
):
    """Get all historical flood events with optional filters"""
    try:
        floods = await HistoricalFloodService.get_all_floods(
            db, skip, limit, severity, start_date, end_date
        )
        return floods
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=FloodStatisticsResponse)
async def get_flood_statistics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get statistical summary of historical floods"""
    try:
        stats = await HistoricalFloodService.get_flood_statistics(db, start_date, end_date)
        return stats
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-decade")
async def get_floods_by_decade(
    db: AsyncSession = Depends(get_db)
):
    """Get count of major floods by decade"""
    try:
        by_decade = await HistoricalFloodService.get_major_floods_by_decade(db)
        return {"floods_by_decade": by_decade}
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{flood_id}", response_model=HistoricalFloodResponse)
async def get_flood_by_id(
    flood_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific historical flood by ID"""
    try:
        flood = await HistoricalFloodService.get_flood_by_id(db, flood_id)
        return flood
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=HistoricalFloodResponse, status_code=201)
async def create_flood(
    flood_data: HistoricalFloodCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new historical flood record"""
    try:
        flood = await HistoricalFloodService.create_flood(db, flood_data.dict())
        return flood
    except DataValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{flood_id}", response_model=HistoricalFloodResponse)
async def update_flood(
    flood_id: int = Path(..., ge=1),
    update_data: HistoricalFloodUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing historical flood record"""
    try:
        flood = await HistoricalFloodService.update_flood(
            db, flood_id, update_data.dict(exclude_unset=True)
        )
        return flood
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{flood_id}", status_code=204)
async def delete_flood(
    flood_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """Delete a historical flood record"""
    try:
        await HistoricalFloodService.delete_flood(db, flood_id)
        return None
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/location/nearby", response_model=List[HistoricalFloodResponse])
async def get_floods_by_location(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(50, ge=1, le=500, description="Search radius in km"),
    db: AsyncSession = Depends(get_db)
):
    """Get historical floods near a location"""
    try:
        floods = await HistoricalFloodService.get_floods_by_location(
            db, lat, lon, radius_km
        )
        return floods
    except DataValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gauge/{gauge_id}", response_model=List[HistoricalFloodResponse])
async def get_floods_by_gauge(
    gauge_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """Get historical floods for a specific gauge"""
    try:
        floods = await HistoricalFloodService.get_floods_by_gauge(db, gauge_id)
        return floods
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{flood_id}/impacts", response_model=FloodImpactResponse, status_code=201)
async def add_flood_impact(
    flood_id: int = Path(..., ge=1),
    impact_data: FloodImpactCreate = ...,
    db: AsyncSession = Depends(get_db)
):
    """Add an impact record to a flood event"""
    try:
        impact = await HistoricalFloodService.add_flood_impact(
            db, flood_id, impact_data.dict()
        )
        return impact
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{flood_id}/impacts", response_model=List[FloodImpactResponse])
async def get_flood_impacts(
    flood_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """Get all impacts for a flood event"""
    try:
        impacts = await HistoricalFloodService.get_flood_impacts(db, flood_id)
        return impacts
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gauge/{gauge_id}/recurrence", response_model=List[RecurrenceIntervalResponse])
async def get_recurrence_intervals(
    gauge_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """Get flood recurrence intervals for a gauge"""
    try:
        recurrences = await HistoricalFloodService.get_recurrence_intervals(db, gauge_id)
        return recurrences
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gauge/{gauge_id}/return-period")
async def calculate_return_period(
    gauge_id: int = Path(..., ge=1),
    discharge_cfs: float = Query(..., ge=0, description="Discharge in cubic feet per second"),
    db: AsyncSession = Depends(get_db)
):
    """Estimate return period for a given discharge"""
    try:
        return_period = await HistoricalFloodService.calculate_return_period(
            db, gauge_id, discharge_cfs
        )

        if return_period is None:
            return {
                "message": "No recurrence data available for this gauge",
                "return_period_years": None
            }

        return {
            "discharge_cfs": discharge_cfs,
            "return_period_years": return_period,
            "probability": 1 / return_period if return_period > 0 else 0
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))