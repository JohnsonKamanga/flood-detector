from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models.prediction import FloodPrediction, RiskZone
from app.models.gauge import RiverGauge
from app.services.flood_predictor import FloodPredictorService
from app.spatial.risk_calculator import FloodRiskCalculator

router = APIRouter()

# Response models
class PredictionResponse(BaseModel):
    id: int
    prediction_time: datetime
    valid_time: datetime
    risk_level: str
    risk_score: float
    confidence: Optional[float]
    rainfall_forecast_in: Optional[float]
    affected_gauges: Optional[dict]

    class Config:
        from_attributes = True

class RiskZoneResponse(BaseModel):
    id: int
    zone_name: str
    base_risk_level: str
    population_estimate: Optional[int]
    elevation_avg_ft: Optional[float]

    class Config:
        from_attributes = True

class CurrentRiskRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 10.0

@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    hours: int = Query(24, description="Hours of predictions to retrieve"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    db: AsyncSession = Depends(get_db)
):
    """Get flood predictions"""

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    query = select(FloodPrediction).where(
        FloodPrediction.prediction_time >= cutoff_time
    )

    if risk_level:
        query = query.where(FloodPrediction.risk_level == risk_level)

    query = query.order_by(desc(FloodPrediction.prediction_time))

    result = await db.execute(query)
    predictions = result.scalars().all()

    return predictions

@router.get("/latest", response_model=PredictionResponse)
async def get_latest_prediction(
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent flood prediction"""

    result = await db.execute(
        select(FloodPrediction)
        .order_by(desc(FloodPrediction.prediction_time))
        .limit(1)
    )

    prediction = result.scalar_one_or_none()

    if not prediction:
        raise HTTPException(status_code=404, detail="No predictions available")

    return prediction

@router.post("/calculate")
async def calculate_current_risk(
    request: CurrentRiskRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate real-time flood risk for a location"""

    try:
        # Initialize services
        predictor = FloodPredictorService()
        calculator = FloodRiskCalculator()

        # Get nearby gauges
        from geoalchemy2.functions import ST_DWithin, ST_MakePoint

        radius_meters = request.radius_km * 1000
        point = ST_MakePoint(request.longitude, request.latitude)

        result = await db.execute(
            select(RiverGauge).where(
                and_(
                    RiverGauge.is_active == True,
                    ST_DWithin(RiverGauge.location, point, radius_meters)
                )
            )
        )

        nearby_gauges = result.scalars().all()

        if not nearby_gauges:
            raise HTTPException(
                status_code=404,
                detail="No active gauges found in the specified area"
            )

        # Prepare gauge data
        gauge_data = [
            {
                'current_gauge_height_ft': g.current_gauge_height_ft,
                'flood_stage_ft': g.flood_stage_ft,
                'action_stage_ft': g.action_stage_ft,
                'last_updated': g.last_updated
            }
            for g in nearby_gauges
        ]

        # Get rainfall forecast
        from app.services.noaa_service import NOAAService

        async with NOAAService() as noaa:
            rainfall_forecast = await noaa.get_forecast_by_point(
                request.latitude,
                request.longitude
            )

        # Estimate soil moisture (simplified - would use actual data in production)
        soil_moisture = 50.0  # Default mid-range value

        # Calculate risk
        risk_assessment = calculator.calculate_composite_risk(
            gauge_data=gauge_data,
            rainfall_forecast=rainfall_forecast,
            soil_moisture=soil_moisture
        )

        return {
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "risk_assessment": risk_assessment,
            "nearby_gauges": [
                {
                    "name": g.name,
                    "usgs_site_id": g.usgs_site_id,
                    "distance_km": round(request.radius_km, 2),
                    "current_stage": g.current_stage
                }
                for g in nearby_gauges
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating risk: {str(e)}"
        )

@router.get("/zones", response_model=List[RiskZoneResponse])
async def get_risk_zones(
    db: AsyncSession = Depends(get_db)
):
    """Get predefined flood risk zones"""

    result = await db.execute(select(RiskZone))
    zones = result.scalars().all()

    return zones

@router.get("/heatmap")
async def get_risk_heatmap(
    bbox: str = Query(..., description="Bounding box: minLon,minLat,maxLon,maxLat"),
    resolution: int = Query(50, description="Grid resolution"),
    db: AsyncSession = Depends(get_db)
):
    """Generate risk heatmap for a geographic area"""

    try:
        # Parse bounding box
        coords = [float(x) for x in bbox.split(',')]
        if len(coords) != 4:
            raise ValueError("Invalid bounding box format")

        min_lon, min_lat, max_lon, max_lat = coords

        # Get gauges in area
        from geoalchemy2.functions import ST_MakeEnvelope

        envelope = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)

        result = await db.execute(
            select(RiverGauge).where(
                and_(
                    RiverGauge.is_active == True,
                    RiverGauge.location.ST_Within(envelope)
                )
            )
        )

        gauges = result.scalars().all()

        if len(gauges) < 3:
            return {
                "error": "Insufficient data points for heatmap generation",
                "gauge_count": len(gauges)
            }

        # Prepare data for interpolation
        gauge_locations = [(g.longitude, g.latitude) for g in gauges]

        # Calculate risk scores for each gauge
        calculator = FloodRiskCalculator()
        risk_scores = []

        for gauge in gauges:
            gauge_data = [{
                'current_gauge_height_ft': gauge.current_gauge_height_ft,
                'flood_stage_ft': gauge.flood_stage_ft,
                'action_stage_ft': gauge.action_stage_ft,
                'last_updated': gauge.last_updated
            }]

            # Simplified calculation for heatmap
            risk = calculator._calculate_gauge_risk(gauge_data)
            risk_scores.append(risk)

        # Generate interpolated grid
        heatmap_data = calculator.generate_risk_zones(
            gauge_locations,
            risk_scores,
            grid_resolution=resolution
        )

        return {
            "bounds": {
                "min_lon": min_lon,
                "min_lat": min_lat,
                "max_lon": max_lon,
                "max_lat": max_lat
            },
            "resolution": resolution,
            "heatmap": heatmap_data,
            "gauge_count": len(gauges),
            "timestamp": datetime.utcnow().isoformat()
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating heatmap: {str(e)}"
        )