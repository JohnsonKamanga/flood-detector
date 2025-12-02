"""
Celery configuration and periodic tasks
"""

import logging
from celery import Celery
from celery.schedules import crontab
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "flood_prediction",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.tasks.scheduled_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


def setup_periodic_tasks():
    """
    Configure periodic tasks
    """

    # Data ingestion every 5 minutes
    celery_app.conf.beat_schedule = {
        'ingest-gauge-data': {
            'task': 'app.tasks.scheduled_tasks.ingest_gauge_data',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
        },
        'ingest-weather-data': {
            'task': 'app.tasks.scheduled_tasks.ingest_weather_data',
            'schedule': crontab(minute='*/15'),  # Every 15 minutes
        },
        'generate-predictions': {
            'task': 'app.tasks.scheduled_tasks.generate_flood_predictions',
            'schedule': crontab(minute='*/10'),  # Every 10 minutes
        },
        'cleanup-old-data': {
            'task': 'app.tasks.scheduled_tasks.cleanup_old_data',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
    }

    logger.info("Periodic tasks configured")


# Celery task for data ingestion
@celery_app.task(name='app.tasks.scheduled_tasks.ingest_gauge_data')
def ingest_gauge_data_task():
    """Periodic task to ingest gauge data"""
    try:
        import asyncio
        from app.services.data_ingestion import DataIngestionService

        async def run():
            service = DataIngestionService()
            await service._ingest_gauge_data()

        asyncio.run(run())
        logger.info("Gauge data ingestion completed")

    except Exception as e:
        logger.error(f"Error in gauge data ingestion task: {e}")
        raise


@celery_app.task(name='app.tasks.scheduled_tasks.ingest_weather_data')
def ingest_weather_data_task():
    """Periodic task to ingest weather data"""
    try:
        import asyncio
        from app.services.data_ingestion import DataIngestionService

        async def run():
            service = DataIngestionService()
            await service._ingest_weather_data()

        asyncio.run(run())
        logger.info("Weather data ingestion completed")

    except Exception as e:
        logger.error(f"Error in weather data ingestion task: {e}")
        raise


@celery_app.task(name='app.tasks.scheduled_tasks.generate_flood_predictions')
def generate_predictions_task():
    """Periodic task to generate flood predictions"""
    try:
        import asyncio
        from app.services.flood_predictor import FloodPredictorService

        async def run():
            service = FloodPredictorService()
            await service.generate_predictions()

        asyncio.run(run())
        logger.info("Flood predictions generated")

    except Exception as e:
        logger.error(f"Error in prediction generation task: {e}")
        raise


@celery_app.task(name='app.tasks.scheduled_tasks.cleanup_old_data')
def cleanup_old_data_task():
    """Periodic task to cleanup old data"""
    try:
        import asyncio
        from datetime import datetime, timedelta
        from app.database import AsyncSessionLocal
        from app.models.gauge import GaugeMeasurement
        from sqlalchemy import delete

        async def run():
            async with AsyncSessionLocal() as db:
                # Delete measurements older than 30 days
                cutoff_date = datetime.utcnow() - timedelta(days=30)

                stmt = delete(GaugeMeasurement).where(
                    GaugeMeasurement.timestamp < cutoff_date
                )

                result = await db.execute(stmt)
                await db.commit()

                logger.info(f"Deleted {result.rowcount} old gauge measurements")

        asyncio.run(run())

    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        raise