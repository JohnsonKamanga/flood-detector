import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

def start_scheduler():
    """Start the background task scheduler"""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
        
        # Add jobs here
        # scheduler.add_job(
        #     some_task,
        #     IntervalTrigger(seconds=settings.data_refresh_interval),
        #     id='data_refresh',
        #     replace_existing=True
        # )

def stop_scheduler():
    """Stop the background task scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
