"""
Spatial database queries and operations
"""

import logging
from typing import List, Tuple, Dict, Optional
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_MakePoint, ST_AsGeoJSON, ST_Contains, ST_Intersects
from app.models.gauge import RiverGauge
from app.models.prediction import RiskZone, FloodPrediction

logger = logging.getLogger(__name__)


class SpatialQueries:
    """
    Spatial query utilities for flood prediction system
    """

    @staticmethod
    async def find_gauges_within_radius(
        db: AsyncSession,
        center_lon: float,
        center_lat: float,
        radius_meters: float
    ) -> List[RiverGauge]:
        """
        Find all gauges within a radius of a point

        Args:
            db: Database session
            center_lon: Center longitude
            center_lat: Center latitude
            radius_meters: Search radius in meters

        Returns:
            List of RiverGauge objects
        """
        try:
            point = ST_MakePoint(center_lon, center_lat)

            query = select(RiverGauge).where(
                and_(
                    RiverGauge.is_active == True,
                    ST_DWithin(RiverGauge.location, point, radius_meters)
                )
            ).order_by(
                ST_Distance(RiverGauge.location, point)
            )

            result = await db.execute(query)
            gauges = result.scalars().all()

            logger.info(f"Found {len(gauges)} gauges within {radius_meters}m of ({center_lat}, {center_lon})")
            return gauges

        except Exception as e:
            logger.error(f"Error finding gauges within radius: {e}")
            return []

    @staticmethod
    async def find_nearest_gauge(
        db: AsyncSession,
        lon: float,
        lat: float
    ) -> Optional[RiverGauge]:
        """
        Find the nearest gauge to a point

        Args:
            db: Database session
            lon: Longitude
            lat: Latitude

        Returns:
            Nearest RiverGauge or None
        """
        try:
            point = ST_MakePoint(lon, lat)

            query = select(RiverGauge).where(
                RiverGauge.is_active == True
            ).order_by(
                ST_Distance(RiverGauge.location, point)
            ).limit(1)

            result = await db.execute(query)
            gauge = result.scalar_one_or_none()

            return gauge

        except Exception as e:
            logger.error(f"Error finding nearest gauge: {e}")
            return None

    @staticmethod
    async def find_gauges_in_bbox(
        db: AsyncSession,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float
    ) -> List[RiverGauge]:
        """
        Find all gauges within a bounding box

        Args:
            db: Database session
            min_lon: Minimum longitude
            min_lat: Minimum latitude
            max_lon: Maximum longitude
            max_lat: Maximum latitude

        Returns:
            List of RiverGauge objects
        """
        try:
            # Create bounding box using raw SQL for better PostGIS support
            bbox_query = text("""
                SELECT * FROM river_gauges
                WHERE is_active = true
                AND ST_Within(
                    location,
                    ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)
                )
            """)

            result = await db.execute(
                bbox_query,
                {
                    "min_lon": min_lon,
                    "min_lat": min_lat,
                    "max_lon": max_lon,
                    "max_lat": max_lat
                }
            )

            gauges = result.fetchall()
            logger.info(f"Found {len(gauges)} gauges in bounding box")

            return gauges

        except Exception as e:
            logger.error(f"Error finding gauges in bbox: {e}")
            return []

    @staticmethod
    async def find_overlapping_risk_zones(
        db: AsyncSession,
        lon: float,
        lat: float
    ) -> List[RiskZone]:
        """
        Find risk zones that contain a given point

        Args:
            db: Database session
            lon: Longitude
            lat: Latitude

        Returns:
            List of overlapping RiskZone objects
        """
        try:
            point = ST_MakePoint(lon, lat)

            query = select(RiskZone).where(
                ST_Contains(RiskZone.geometry, point)
            )

            result = await db.execute(query)
            zones = result.scalars().all()

            return zones

        except Exception as e:
            logger.error(f"Error finding overlapping risk zones: {e}")
            return []

    @staticmethod
    async def calculate_distance_between_gauges(
        db: AsyncSession,
        gauge_id_1: int,
        gauge_id_2: int
    ) -> Optional[float]:
        """
        Calculate distance between two gauges in meters

        Args:
            db: Database session
            gauge_id_1: First gauge ID
            gauge_id_2: Second gauge ID

        Returns:
            Distance in meters or None if error
        """
        try:
            query = text("""
                SELECT ST_Distance(
                    g1.location::geography,
                    g2.location::geography
                ) as distance
                FROM river_gauges g1, river_gauges g2
                WHERE g1.id = :id1 AND g2.id = :id2
            """)

            result = await db.execute(query, {"id1": gauge_id_1, "id2": gauge_id_2})
            row = result.fetchone()

            if row:
                return float(row[0])
            return None

        except Exception as e:
            logger.error(f"Error calculating distance between gauges: {e}")
            return None

    @staticmethod
    async def get_gauge_geojson(
        db: AsyncSession,
        gauge_id: int
    ) -> Optional[Dict]:
        """
        Get gauge location as GeoJSON

        Args:
            db: Database session
            gauge_id: Gauge ID

        Returns:
            GeoJSON dictionary or None
        """
        try:
            query = text("""
                SELECT 
                    id,
                    name,
                    usgs_site_id,
                    ST_AsGeoJSON(location) as geojson,
                    current_stage,
                    current_gauge_height_ft
                FROM river_gauges
                WHERE id = :gauge_id
            """)

            result = await db.execute(query, {"gauge_id": gauge_id})
            row = result.fetchone()

            if row:
                import json
                return {
                    "type": "Feature",
                    "geometry": json.loads(row[3]),
                    "properties": {
                        "id": row[0],
                        "name": row[1],
                        "usgs_site_id": row[2],
                        "current_stage": row[4],
                        "current_gauge_height_ft": row[5]
                    }
                }
            return None

        except Exception as e:
            logger.error(f"Error getting gauge GeoJSON: {e}")
            return None

    @staticmethod
    async def find_high_risk_areas(
        db: AsyncSession,
        min_risk_score: float = 50.0
    ) -> List[Dict]:
        """
        Find areas with high flood risk

        Args:
            db: Database session
            min_risk_score: Minimum risk score threshold

        Returns:
            List of high-risk area dictionaries
        """
        try:
            query = text("""
                SELECT 
                    p.id,
                    p.risk_level,
                    p.risk_score,
                    ST_AsGeoJSON(p.risk_area) as geojson,
                    p.prediction_time
                FROM flood_predictions p
                WHERE p.risk_score >= :min_score
                AND p.prediction_time >= NOW() - INTERVAL '24 hours'
                ORDER BY p.risk_score DESC
            """)

            result = await db.execute(query, {"min_score": min_risk_score})
            rows = result.fetchall()

            import json
            areas = []
            for row in rows:
                areas.append({
                    "id": row[0],
                    "risk_level": row[1],
                    "risk_score": row[2],
                    "geometry": json.loads(row[3]) if row[3] else None,
                    "prediction_time": row[4].isoformat() if row[4] else None
                })

            logger.info(f"Found {len(areas)} high-risk areas")
            return areas

        except Exception as e:
            logger.error(f"Error finding high-risk areas: {e}")
            return []

    @staticmethod
    async def calculate_affected_population(
        db: AsyncSession,
        risk_area_geojson: str
    ) -> int:
        """
        Estimate population affected by a risk area
        Simplified calculation based on risk zones

        Args:
            db: Database session
            risk_area_geojson: GeoJSON string of risk area

        Returns:
            Estimated affected population
        """
        try:
            query = text("""
                SELECT SUM(rz.population_estimate)
                FROM risk_zones rz
                WHERE ST_Intersects(
                    rz.geometry,
                    ST_GeomFromGeoJSON(:geojson)
                )
            """)

            result = await db.execute(query, {"geojson": risk_area_geojson})
            row = result.fetchone()

            return int(row[0]) if row and row[0] else 0

        except Exception as e:
            logger.error(f"Error calculating affected population: {e}")
            return 0