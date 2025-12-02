import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import delete

from app.config import settings
from app.services.data_ingestion import DataIngestionService
from app.services.flood_predictor import FloodPredictorService
from app.database import AsyncSessionLocal
from app.models.gauge import GaugeMeasurement

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def ingest_gauge_data():
    """Periodic task to ingest gauge data"""
    try:
        service = DataIngestionService()
        await service._ingest_gauge_data()
        logger.info("Gauge data ingestion completed")
    except Exception as e:
        logger.error(f"Error in gauge data ingestion task: {e}")

async def ingest_weather_data():
    """Periodic task to ingest weather data"""
    try:
        service = DataIngestionService()
        await service._ingest_weather_data()
        logger.info("Weather data ingestion completed")
    except Exception as e:
        logger.error(f"Error in weather data ingestion task: {e}")

async def generate_predictions():
    """Periodic task to generate flood predictions"""
    try:
        service = FloodPredictorService()
        await service.generate_predictions()
        logger.info("Flood predictions generated")
    except Exception as e:
        logger.error(f"Error in prediction generation task: {e}")

async def cleanup_old_data():
    """Periodic task to cleanup old data"""
    try:
        async with AsyncSessionLocal() as db:
            # Delete measurements older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)

            stmt = delete(GaugeMeasurement).where(
                GaugeMeasurement.timestamp < cutoff_date
            )

            result = await db.execute(stmt)
            await db.commit()

            logger.info(f"Deleted {result.rowcount} old gauge measurements")
    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")

def start_scheduler():
    """Start the background task scheduler"""
    if not scheduler.running:
        # Ingest gauge data every 5 minutes
        scheduler.add_job(
            ingest_gauge_data,
            IntervalTrigger(minutes=5),
            id='ingest_gauge_data',
            replace_existing=True
        )

        # Ingest weather data every 15 minutes
        scheduler.add_job(
            ingest_weather_data,
            IntervalTrigger(minutes=15),
            id='ingest_weather_data',
            replace_existing=True
        )

        # Generate predictions every 10 minutes
        scheduler.add_job(
            generate_predictions,
            IntervalTrigger(minutes=10),
            id='generate_predictions',
            replace_existing=True
        )

        # Cleanup old data daily at 2 AM
        scheduler.add_job(
            cleanup_old_data,
            CronTrigger(hour=2, minute=0),
            id='cleanup_old_data',
            replace_existing=True
        )

        scheduler.start()
        logger.info("Scheduler started with periodic tasks")

def stop_scheduler():
    """Stop the background task scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
