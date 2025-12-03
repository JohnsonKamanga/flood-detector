import logging
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.prediction import FloodPrediction
from app.models.gauge import RiverGauge
from app.spatial.risk_calculator import FloodRiskCalculator
from app.services.noaa_service import NOAAService
from app.routes.websocket import broadcast_prediction_update, broadcast_risk_alert

logger = logging.getLogger(__name__)

class FloodPredictorService:
    """Service for generating flood predictions"""

    def __init__(self):
        self.risk_calculator = FloodRiskCalculator()

    async def generate_predictions(self):
        """Generate flood predictions for all monitored areas"""
        async with AsyncSessionLocal() as db:
            try:
                from sqlalchemy import select

                # Get all active gauges
                result = await db.execute(
                    select(RiverGauge).where(RiverGauge.is_active == True)
                )
                gauges = result.scalars().all()

                if not gauges:
                    logger.warning("No active gauges for prediction")
                    return

                # Group gauges by region for area-based predictions
                predictions = []

                # For simplicity, create one prediction per gauge
                for gauge in gauges:
                    try:
                        prediction = await self._predict_for_gauge(db, gauge)
                        if prediction:
                            predictions.append(prediction)

                    except Exception as e:
                        logger.error(f"Error predicting for gauge {gauge.usgs_site_id}: {e}")
                        continue

                # Commit all predictions
                await db.commit()

                logger.info(f"Generated {len(predictions)} predictions")

                # Broadcast high-risk predictions
                for pred in predictions:
                    if pred.risk_level in ['high', 'severe']:
                        await broadcast_risk_alert({
                            "prediction_id": pred.id,
                            "risk_level": pred.risk_level,
                            "risk_score": pred.risk_score,
                            "affected_gauges": pred.affected_gauges,
                            "timestamp": pred.prediction_time.isoformat()
                        })

            except Exception as e:
                logger.error(f"Error generating predictions: {e}", exc_info=True)
                await db.rollback()

    async def _predict_for_gauge(
        self, 
        db: AsyncSession, 
        gauge: RiverGauge
    ) -> FloodPrediction:
        """Generate prediction for a specific gauge"""

        start_time = datetime.utcnow()

        # Prepare gauge data with safe defaults for None values
        gauge_data = [{
            'current_gauge_height_ft': gauge.current_gauge_height_ft or 0.0,
            'flood_stage_ft': gauge.flood_stage_ft or 20.0,
            'action_stage_ft': gauge.action_stage_ft or 10.0,
            'last_updated': gauge.last_updated
        }]

        # Get weather forecast (may fail for international locations)
        rainfall_forecast = None
        try:
            # Try NOAA first (US only), fallback to Open-Meteo (global)
            from app.services.openmeteo_service import get_weather_forecast
            rainfall_forecast = await get_weather_forecast(
                gauge.latitude,
                gauge.longitude,
                prefer_noaa=True  # Try NOAA first for US locations
            )
        except Exception as e:
            # Both weather sources failed
            logger.warning(f"Weather forecast unavailable for gauge {gauge.usgs_site_id}: {e}")
            # Continue with prediction using default/estimated values

        # Estimate soil moisture (simplified)
        soil_moisture = 50.0

        # Calculate risk
        risk_assessment = self.risk_calculator.calculate_composite_risk(
            gauge_data=gauge_data,
            rainfall_forecast=rainfall_forecast or {},  # Empty dict if no forecast
            soil_moisture=soil_moisture
        )

        # Calculate total forecast rainfall
        total_rainfall = 0
        if rainfall_forecast and rainfall_forecast.get('periods'):
            for period in rainfall_forecast['periods'][:8]:
                if 'precipitation_amount' in period and period['precipitation_amount'] is not None:
                    total_rainfall += period['precipitation_amount']
                else:
                    prob = period.get('precipitation_probability', 0) or 0
                    total_rainfall += (prob / 100) * 0.1

        # Create prediction record
        prediction = FloodPrediction(
            prediction_time=datetime.utcnow(),
            valid_time=datetime.utcnow() + timedelta(hours=24),
            risk_level=risk_assessment['risk_level'],
            risk_score=risk_assessment['composite_score'],
            confidence=risk_assessment['confidence'],
            affected_gauges={'gauge_ids': [gauge.id]},
            rainfall_forecast_in=round(total_rainfall, 2),
            soil_saturation_pct=soil_moisture,
            upstream_flow_cfs=gauge.current_flow_cfs or 0.0,
            model_version='1.0',
            processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
        )

        db.add(prediction)

        # Broadcast update
        await broadcast_prediction_update({
            "gauge_id": gauge.id,
            "gauge_name": gauge.name,
            "risk_level": prediction.risk_level,
            "risk_score": prediction.risk_score,
            "confidence": prediction.confidence,
            "prediction_time": prediction.prediction_time.isoformat()
        })

        return prediction