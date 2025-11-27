import asyncio
import logging
from typing import List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.gauge import RiverGauge, GaugeMeasurement
from app.services.usgs_service import USGSService
from app.services.noaa_service import NOAAService
from app.routes.websocket import broadcast_gauge_update
from app.config import settings

logger = logging.getLogger(__name__)

class DataIngestionService:
    """Background service for continuous data ingestion"""

    def __init__(self):
        self.refresh_interval = settings.data_refresh_interval
        self.running = False
        self.task = None

    async def start(self):
        """Start the data ingestion service"""
        if self.running:
            logger.warning("Data ingestion service already running")
            return

        self.running = True
        self.task = asyncio.create_task(self._ingestion_loop())
        logger.info("Data ingestion service started")

    async def stop(self):
        """Stop the data ingestion service"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Data ingestion service stopped")

    async def _ingestion_loop(self):
        """Main ingestion loop"""
        while self.running:
            try:
                logger.info("Starting data ingestion cycle")

                # Ingest gauge data
                await self._ingest_gauge_data()

                # Ingest weather data
                await self._ingest_weather_data()

                logger.info(f"Data ingestion complete. Next cycle in {self.refresh_interval}s")

                # Wait before next cycle
                await asyncio.sleep(self.refresh_interval)

            except Exception as e:
                logger.error(f"Error in ingestion loop: {e}", exc_info=True)
                # Wait before retrying
                await asyncio.sleep(60)

    async def _ingest_gauge_data(self):
        """Ingest data from USGS gauges"""
        async with AsyncSessionLocal() as db:
            try:
                # Get all active gauges
                from sqlalchemy import select
                result = await db.execute(
                    select(RiverGauge).where(RiverGauge.is_active == True)
                )
                gauges = result.scalars().all()

                if not gauges:
                    logger.warning("No active gauges found")
                    return

                # Fetch data from USGS in batches
                batch_size = 20
                site_codes = [g.usgs_site_id for g in gauges]

                async with USGSService() as usgs:
                    for i in range(0, len(site_codes), batch_size):
                        batch = site_codes[i:i + batch_size]

                        try:
                            data = await usgs.get_site_data(batch)

                            # Update gauges with fresh data
                            for gauge in gauges:
                                if gauge.usgs_site_id in data:
                                    await self._update_gauge(db, gauge, data[gauge.usgs_site_id])

                            await db.commit()

                        except Exception as e:
                            logger.error(f"Error fetching batch {i}-{i+batch_size}: {e}")
                            continue

                logger.info(f"Updated {len(gauges)} gauges")

            except Exception as e:
                logger.error(f"Error ingesting gauge data: {e}", exc_info=True)
                await db.rollback()

    async def _update_gauge(self, db: AsyncSession, gauge: RiverGauge, site_data: Dict):
        """Update gauge with fresh data"""
        try:
            measurements = site_data.get('measurements', [])

            if not measurements:
                return

            # Group measurements by timestamp
            by_timestamp = {}
            for m in measurements:
                ts = m['timestamp']
                if ts not in by_timestamp:
                    by_timestamp[ts] = {}

                param = m['parameter']
                if param == '00060':  # Discharge
                    by_timestamp[ts]['flow_cfs'] = m['value']
                elif param == '00065':  # Gauge height
                    by_timestamp[ts]['gauge_height_ft'] = m['value']

            # Get latest measurement
            latest_ts = max(by_timestamp.keys())
            latest = by_timestamp[latest_ts]

            # Update gauge current values
            if 'flow_cfs' in latest:
                gauge.current_flow_cfs = latest['flow_cfs']

            if 'gauge_height_ft' in latest:
                gauge.current_gauge_height_ft = latest['gauge_height_ft']

                # Determine stage
                height = latest['gauge_height_ft']
                if gauge.major_flood_stage_ft and height >= gauge.major_flood_stage_ft:
                    gauge.current_stage = 'major'
                elif gauge.flood_stage_ft and height >= gauge.flood_stage_ft:
                    gauge.current_stage = 'flood'
                elif gauge.action_stage_ft and height >= gauge.action_stage_ft:
                    gauge.current_stage = 'action'
                else:
                    gauge.current_stage = 'normal'

            gauge.last_updated = latest_ts

            # Create measurement record
            measurement = GaugeMeasurement(
                gauge_id=gauge.id,
                timestamp=latest_ts,
                flow_cfs=latest.get('flow_cfs'),
                gauge_height_ft=latest.get('gauge_height_ft')
            )
            db.add(measurement)

            # Broadcast update via WebSocket
            await broadcast_gauge_update({
                "gauge_id": gauge.id,
                "usgs_site_id": gauge.usgs_site_id,
                "name": gauge.name,
                "current_flow_cfs": gauge.current_flow_cfs,
                "current_gauge_height_ft": gauge.current_gauge_height_ft,
                "current_stage": gauge.current_stage,
                "last_updated": gauge.last_updated.isoformat()
            })

        except Exception as e:
            logger.error(f"Error updating gauge {gauge.usgs_site_id}: {e}")

    async def _ingest_weather_data(self):
        """Ingest weather forecast data"""
        async with AsyncSessionLocal() as db:
            try:
                # Get gauges to fetch weather for
                from sqlalchemy import select
                result = await db.execute(
                    select(RiverGauge)
                    .where(RiverGauge.is_active == True)
                    .limit(10)  # Sample subset for weather data
                )
                gauges = result.scalars().all()

                async with NOAAService() as noaa:
                    for gauge in gauges:
                        try:
                            # Get precipitation data
                            precip_data = await noaa.get_precipitation_data(
                                gauge.latitude,
                                gauge.longitude,
                                hours=24
                            )

                            # Update measurement with precipitation
                            if precip_data and precip_data.get('observations'):
                                latest_obs = precip_data['observations'][0]

                                # Find or create measurement for this timestamp
                                from sqlalchemy import and_
                                obs_time = datetime.fromisoformat(
                                    latest_obs['timestamp'].replace('Z', '+00:00')
                                )

                                result = await db.execute(
                                    select(GaugeMeasurement).where(
                                        and_(
                                            GaugeMeasurement.gauge_id == gauge.id,
                                            GaugeMeasurement.timestamp == obs_time
                                        )
                                    )
                                )
                                measurement = result.scalar_one_or_none()

                                if measurement:
                                    measurement.precipitation_in = latest_obs.get('precipitation_in', 0)
                                    measurement.temperature_f = latest_obs.get('temperature')

                            # Small delay to avoid rate limiting
                            await asyncio.sleep(0.5)

                        except Exception as e:
                            logger.error(f"Error fetching weather for gauge {gauge.usgs_site_id}: {e}")
                            continue

                await db.commit()
                logger.info("Weather data ingestion complete")

            except Exception as e:
                logger.error(f"Error ingesting weather data: {e}", exc_info=True)
                await db.rollback()