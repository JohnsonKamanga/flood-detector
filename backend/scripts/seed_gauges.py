import asyncio
import logging
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import AsyncSessionLocal
from app.models.gauge import RiverGauge
from app.services.usgs_service import USGSService
from sqlalchemy import select
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample gauges (Austin, TX area)
SAMPLE_SITES = [
    '08155200', # Barton Ck at Loop 360, Austin, TX
    '08155300', # Barton Ck at Lost Ck Blvd, Austin, TX
    '08155400', # Barton Ck at Loop 360, Austin, TX
    '08158000', # Colorado Rv at Bastrop, TX
    '08151500', # Colorado Rv at Austin, TX
]

# Manual gauges (International/Custom)
MANUAL_GAUGES = [
    {
        "usgs_site_id": "MANUAL_SL_01",
        "name": "Sri Lanka Monitor",
        "latitude": 8.006250,
        "longitude": 80.539583
    },
    {
        "usgs_site_id": "MANUAL_MW_01",
        "name": "Malawi River Monitor",
        "latitude": -16.0, # Shire River area
        "longitude": 35.0
    }
]

async def seed_gauges():
    logger.info("Starting gauge seeding...")
    
    async with AsyncSessionLocal() as db:
        # Check if gauges exist
        result = await db.execute(select(RiverGauge))
        existing = result.scalars().all()
        existing_ids = {g.usgs_site_id for g in existing}
        
        count = 0

        # 1. Process Manual Gauges
        for gauge_info in MANUAL_GAUGES:
            if gauge_info['usgs_site_id'] in existing_ids:
                logger.info(f"Skipping existing manual gauge: {gauge_info['name']}")
                continue

            try:
                logger.info(f"Adding manual gauge: {gauge_info['name']}")
                gauge = RiverGauge(
                    usgs_site_id=gauge_info['usgs_site_id'],
                    name=gauge_info['name'],
                    latitude=gauge_info['latitude'],
                    longitude=gauge_info['longitude'],
                    location=from_shape(Point(gauge_info['longitude'], gauge_info['latitude']), srid=4326),
                    is_active=True,
                    action_stage_ft=10.0,
                    flood_stage_ft=20.0,
                    major_flood_stage_ft=30.0
                )
                db.add(gauge)
                count += 1
            except Exception as e:
                logger.error(f"Error adding manual gauge {gauge_info['name']}: {e}")

        # 2. Process USGS Gauges
        sites_to_fetch = [s for s in SAMPLE_SITES if s not in existing_ids]
        
        if sites_to_fetch:
            logger.info(f"Fetching metadata for {len(sites_to_fetch)} USGS sites...")
            async with USGSService() as usgs:
                # Fetch metadata
                data = await usgs.get_site_data(sites_to_fetch)
                
                if data:
                    for site_code, info in data.items():
                        try:
                            logger.info(f"Adding USGS gauge: {info['site_name']} ({site_code})")
                            
                            # Create gauge
                            gauge = RiverGauge(
                                usgs_site_id=site_code,
                                name=info['site_name'],
                                latitude=info['latitude'],
                                longitude=info['longitude'],
                                location=from_shape(Point(info['longitude'], info['latitude']), srid=4326),
                                is_active=True,
                                # Set default thresholds (these would ideally come from NWS/AHPS)
                                action_stage_ft=10.0,
                                flood_stage_ft=20.0,
                                major_flood_stage_ft=30.0
                            )
                            
                            db.add(gauge)
                            count += 1
                            
                        except Exception as e:
                            logger.error(f"Error adding gauge {site_code}: {e}")
                else:
                    logger.error("Failed to fetch data from USGS")
        else:
            logger.info("All USGS sites already exist.")

        await db.commit()
        logger.info(f"Successfully added {count} new gauges")

if __name__ == "__main__":
    asyncio.run(seed_gauges())
