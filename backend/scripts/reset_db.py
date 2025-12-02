import asyncio
import logging
import sys
import os
from sqlalchemy import text

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_db():
    logger.info("Dropping river_gauges table...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS river_gauges CASCADE"))
    logger.info("Table dropped.")

if __name__ == "__main__":
    asyncio.run(reset_db())
