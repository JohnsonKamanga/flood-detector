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
    '07010000', # Mississippi River at St. Louis, MO
    '09380000', # Colorado River at Lees Ferry, AZ
    '01646500', # Potomac River near Washington, DC
    '01100000', # Merrimack River near Lowell, MA
]

# Manual gauges (International/Custom High-Risk Areas)
MANUAL_GAUGES = [
    # Asia - High Risk Flood Zones
    {
        "usgs_site_id": "MANUAL_SL_01",
        "name": "Kelani River at Colombo, Sri Lanka",
        "latitude": 6.9271,
        "longitude": 79.8612
    },
    {
        "usgs_site_id": "MANUAL_BD_01",
        "name": "Brahmaputra River at Dhaka, Bangladesh",
        "latitude": 23.8103,
        "longitude": 90.4125
    },
    {
        "usgs_site_id": "MANUAL_IN_01",
        "name": "Ganges River at Varanasi, India",
        "latitude": 25.3176,
        "longitude": 82.9739
    },
    {
        "usgs_site_id": "MANUAL_PK_01",
        "name": "Indus River at Karachi, Pakistan",
        "latitude": 24.8607,
        "longitude": 67.0011
    },
    {
        "usgs_site_id": "MANUAL_TH_01",
        "name": "Chao Phraya River at Bangkok, Thailand",
        "latitude": 13.7563,
        "longitude": 100.5018
    },
    {
        "usgs_site_id": "MANUAL_VN_01",
        "name": "Mekong River at Ho Chi Minh City, Vietnam",
        "latitude": 10.8231,
        "longitude": 106.6297
    },
    
    # Africa - High Risk Flood Zones
    {
        "usgs_site_id": "MANUAL_MW_01",
        "name": "Shire River at Blantyre, Malawi",
        "latitude": -15.7861,
        "longitude": 35.0058
    },
    {
        "usgs_site_id": "MANUAL_NG_01",
        "name": "Niger River at Lagos, Nigeria",
        "latitude": 6.5244,
        "longitude": 3.3792
    },
    {
        "usgs_site_id": "MANUAL_EG_01",
        "name": "Nile River at Cairo, Egypt",
        "latitude": 30.0444,
        "longitude": 31.2357
    },
    {
        "usgs_site_id": "MANUAL_MZ_01",
        "name": "Zambezi River at Tete, Mozambique",
        "latitude": -16.1564,
        "longitude": 33.5867
    },
    
    # South America - High Risk Flood Zones
    {
        "usgs_site_id": "MANUAL_BR_01",
        "name": "Amazon River at Manaus, Brazil",
        "latitude": -3.1190,
        "longitude": -60.0217
    },
    {
        "usgs_site_id": "MANUAL_AR_01",
        "name": "Paraná River at Buenos Aires, Argentina",
        "latitude": -34.6037,
        "longitude": -58.3816
    },
    {
        "usgs_site_id": "MANUAL_CO_01",
        "name": "Magdalena River at Barranquilla, Colombia",
        "latitude": 10.9685,
        "longitude": -74.7813
    },
    
    # Europe - High Risk Flood Zones
    {
        "usgs_site_id": "MANUAL_DE_01",
        "name": "Rhine River at Cologne, Germany",
        "latitude": 50.9375,
        "longitude": 6.9603
    },
    {
        "usgs_site_id": "MANUAL_IT_01",
        "name": "Po River at Venice, Italy",
        "latitude": 45.4408,
        "longitude": 12.3155
    },
    {
        "usgs_site_id": "MANUAL_UK_01",
        "name": "Thames River at London, UK",
        "latitude": 51.5074,
        "longitude": -0.1278
    },
    
    # North America - Additional High Risk Areas
    {
        "usgs_site_id": "MANUAL_US_01",
        "name": "Mississippi River at New Orleans, Louisiana",
        "latitude": 29.9511,
        "longitude": -90.0715
    },
    {
        "usgs_site_id": "MANUAL_US_02",
        "name": "Houston Ship Channel, Texas",
        "latitude": 29.7604,
        "longitude": -95.3698
    },
    {
        "usgs_site_id": "MANUAL_US_03",
        "name": "Miami River at Miami, Florida",
        "latitude": 25.7617,
        "longitude": -80.1918
    },
    
    # Australia/Oceania - High Risk Flood Zones
    {
        "usgs_site_id": "MANUAL_AU_01",
        "name": "Brisbane River at Brisbane, Australia",
        "latitude": -27.4698,
        "longitude": 153.0251
    },
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
