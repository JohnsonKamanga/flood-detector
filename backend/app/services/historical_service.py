"""
Service for managing historical flood data
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_AsGeoJSON, ST_MakePoint, ST_DWithin

from app.models.historical import (
    HistoricalFlood,
    FloodEvent,
    FloodImpact,
    FloodRecurrence,
    FloodDamageFunction
)
from app.models.gauge import RiverGauge
from app.utils.exceptions import (
    ResourceNotFoundError,
    DataValidationError,
    DatabaseError
)
from app.utils.validators import validate_coordinates, validate_date_range

logger = logging.getLogger(__name__)


class HistoricalFloodService:
    """Service for historical flood data operations"""

    @staticmethod
    async def get_all_floods(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[HistoricalFlood]:
        """
        Get all historical floods with optional filters

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            severity: Filter by severity level
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            List of HistoricalFlood objects
        """
        try:
            query = select(HistoricalFlood)

            # Apply filters
            conditions = []

            if severity:
                conditions.append(HistoricalFlood.severity == severity)

            if start_date:
                conditions.append(HistoricalFlood.event_date >= start_date)

            if end_date:
                conditions.append(HistoricalFlood.event_date <= end_date)

            if conditions:
                query = query.where(and_(*conditions))

            query = query.order_by(desc(HistoricalFlood.event_date)).offset(skip).limit(limit)

            result = await db.execute(query)
            floods = result.scalars().all()

            logger.info(f"Retrieved {len(floods)} historical floods")
            return floods

        except Exception as e:
            logger.error(f"Error retrieving historical floods: {e}")
            raise DatabaseError(f"Failed to retrieve historical floods: {str(e)}")

    @staticmethod
    async def get_flood_by_id(
        db: AsyncSession,
        flood_id: int
    ) -> HistoricalFlood:
        """
        Get a specific historical flood by ID

        Args:
            db: Database session
            flood_id: Flood ID

        Returns:
            HistoricalFlood object

        Raises:
            ResourceNotFoundError: If flood not found
        """
        try:
            query = select(HistoricalFlood).where(HistoricalFlood.id == flood_id)
            result = await db.execute(query)
            flood = result.scalar_one_or_none()

            if not flood:
                raise ResourceNotFoundError("HistoricalFlood", flood_id)

            return flood

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving flood {flood_id}: {e}")
            raise DatabaseError(f"Failed to retrieve flood: {str(e)}")

    @staticmethod
    async def create_flood(
        db: AsyncSession,
        flood_data: Dict
    ) -> HistoricalFlood:
        """
        Create a new historical flood record

        Args:
            db: Database session
            flood_data: Dictionary with flood information

        Returns:
            Created HistoricalFlood object
        """
        try:
            # Validate required fields
            required_fields = ['event_name', 'event_date', 'severity']
            for field in required_fields:
                if field not in flood_data:
                    raise DataValidationError(f"Missing required field: {field}")

            # Create flood record
            flood = HistoricalFlood(**flood_data)
            db.add(flood)
            await db.commit()
            await db.refresh(flood)

            logger.info(f"Created historical flood: {flood.event_name}")
            return flood

        except DataValidationError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating historical flood: {e}")
            raise DatabaseError(f"Failed to create flood record: {str(e)}")

    @staticmethod
    async def update_flood(
        db: AsyncSession,
        flood_id: int,
        update_data: Dict
    ) -> HistoricalFlood:
        """
        Update an existing historical flood record

        Args:
            db: Database session
            flood_id: Flood ID
            update_data: Dictionary with updated information

        Returns:
            Updated HistoricalFlood object
        """
        try:
            flood = await HistoricalFloodService.get_flood_by_id(db, flood_id)

            # Update fields
            for key, value in update_data.items():
                if hasattr(flood, key):
                    setattr(flood, key, value)

            flood.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(flood)

            logger.info(f"Updated historical flood {flood_id}")
            return flood

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating flood {flood_id}: {e}")
            raise DatabaseError(f"Failed to update flood: {str(e)}")

    @staticmethod
    async def delete_flood(
        db: AsyncSession,
        flood_id: int
    ) -> bool:
        """
        Delete a historical flood record

        Args:
            db: Database session
            flood_id: Flood ID

        Returns:
            True if successful
        """
        try:
            flood = await HistoricalFloodService.get_flood_by_id(db, flood_id)
            await db.delete(flood)
            await db.commit()

            logger.info(f"Deleted historical flood {flood_id}")
            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting flood {flood_id}: {e}")
            raise DatabaseError(f"Failed to delete flood: {str(e)}")

    @staticmethod
    async def get_floods_by_location(
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 50.0
    ) -> List[HistoricalFlood]:
        """
        Get historical floods near a location

        Args:
            db: Database session
            latitude: Latitude
            longitude: Longitude
            radius_km: Search radius in kilometers

        Returns:
            List of HistoricalFlood objects
        """
        try:
            validate_coordinates(latitude, longitude)

            point = ST_MakePoint(longitude, latitude)
            radius_meters = radius_km * 1000

            query = select(HistoricalFlood).where(
                ST_DWithin(HistoricalFlood.geometry, point, radius_meters)
            ).order_by(desc(HistoricalFlood.event_date))

            result = await db.execute(query)
            floods = result.scalars().all()

            logger.info(f"Found {len(floods)} floods near ({latitude}, {longitude})")
            return floods

        except Exception as e:
            logger.error(f"Error finding floods by location: {e}")
            raise DatabaseError(f"Failed to find floods: {str(e)}")

    @staticmethod
    async def get_floods_by_gauge(
        db: AsyncSession,
        gauge_id: int
    ) -> List[HistoricalFlood]:
        """
        Get historical floods for a specific gauge

        Args:
            db: Database session
            gauge_id: Gauge ID

        Returns:
            List of HistoricalFlood objects
        """
        try:
            query = select(HistoricalFlood).where(
                HistoricalFlood.gauge_id == gauge_id
            ).order_by(desc(HistoricalFlood.event_date))

            result = await db.execute(query)
            floods = result.scalars().all()

            return floods

        except Exception as e:
            logger.error(f"Error retrieving floods for gauge {gauge_id}: {e}")
            raise DatabaseError(f"Failed to retrieve floods: {str(e)}")

    @staticmethod
    async def get_flood_statistics(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get statistical summary of historical floods

        Args:
            db: Database session
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Dictionary with statistics
        """
        try:
            query = select(HistoricalFlood)

            if start_date:
                query = query.where(HistoricalFlood.event_date >= start_date)
            if end_date:
                query = query.where(HistoricalFlood.event_date <= end_date)

            result = await db.execute(query)
            floods = result.scalars().all()

            if not floods:
                return {
                    'total_events': 0,
                    'by_severity': {},
                    'total_damage_usd': 0,
                    'total_casualties': 0,
                    'total_evacuations': 0
                }

            # Calculate statistics
            severity_counts = {}
            total_damage = 0
            total_casualties = 0
            total_evacuations = 0

            for flood in floods:
                # Count by severity
                severity = flood.severity or 'unknown'
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

                # Sum damages
                if flood.estimated_damage_usd:
                    total_damage += flood.estimated_damage_usd

                if flood.casualties:
                    total_casualties += flood.casualties

                if flood.evacuations:
                    total_evacuations += flood.evacuations

            return {
                'total_events': len(floods),
                'by_severity': severity_counts,
                'total_damage_usd': total_damage,
                'total_casualties': total_casualties,
                'total_evacuations': total_evacuations,
                'average_damage_per_event': total_damage / len(floods) if floods else 0
            }

        except Exception as e:
            logger.error(f"Error calculating flood statistics: {e}")
            raise DatabaseError(f"Failed to calculate statistics: {str(e)}")

    @staticmethod
    async def add_flood_impact(
        db: AsyncSession,
        flood_id: int,
        impact_data: Dict
    ) -> FloodImpact:
        """
        Add an impact record to a flood event

        Args:
            db: Database session
            flood_id: Flood ID
            impact_data: Impact information

        Returns:
            Created FloodImpact object
        """
        try:
            # Verify flood exists
            await HistoricalFloodService.get_flood_by_id(db, flood_id)

            # Create impact
            impact = FloodImpact(
                historical_flood_id=flood_id,
                **impact_data
            )
            db.add(impact)
            await db.commit()
            await db.refresh(impact)

            logger.info(f"Added impact to flood {flood_id}")
            return impact

        except Exception as e:
            await db.rollback()
            logger.error(f"Error adding flood impact: {e}")
            raise DatabaseError(f"Failed to add impact: {str(e)}")

    @staticmethod
    async def get_flood_impacts(
        db: AsyncSession,
        flood_id: int
    ) -> List[FloodImpact]:
        """
        Get all impacts for a flood event

        Args:
            db: Database session
            flood_id: Flood ID

        Returns:
            List of FloodImpact objects
        """
        try:
            query = select(FloodImpact).where(
                FloodImpact.historical_flood_id == flood_id
            ).order_by(FloodImpact.created_at)

            result = await db.execute(query)
            impacts = result.scalars().all()

            return impacts

        except Exception as e:
            logger.error(f"Error retrieving flood impacts: {e}")
            raise DatabaseError(f"Failed to retrieve impacts: {str(e)}")

    @staticmethod
    async def get_recurrence_intervals(
        db: AsyncSession,
        gauge_id: int
    ) -> List[FloodRecurrence]:
        """
        Get flood recurrence intervals for a gauge

        Args:
            db: Database session
            gauge_id: Gauge ID

        Returns:
            List of FloodRecurrence objects
        """
        try:
            query = select(FloodRecurrence).where(
                FloodRecurrence.gauge_id == gauge_id
            ).order_by(FloodRecurrence.return_period_years)

            result = await db.execute(query)
            recurrences = result.scalars().all()

            return recurrences

        except Exception as e:
            logger.error(f"Error retrieving recurrence intervals: {e}")
            raise DatabaseError(f"Failed to retrieve recurrence intervals: {str(e)}")

    @staticmethod
    async def calculate_return_period(
        db: AsyncSession,
        gauge_id: int,
        discharge_cfs: float
    ) -> Optional[int]:
        """
        Estimate return period for a given discharge

        Args:
            db: Database session
            gauge_id: Gauge ID
            discharge_cfs: Discharge in cubic feet per second

        Returns:
            Estimated return period in years, or None
        """
        try:
            recurrences = await HistoricalFloodService.get_recurrence_intervals(db, gauge_id)

            if not recurrences:
                return None

            # Find closest match
            for recurrence in recurrences:
                if discharge_cfs <= recurrence.discharge_cfs:
                    return recurrence.return_period_years

            # If discharge exceeds all known values
            return recurrences[-1].return_period_years

        except Exception as e:
            logger.error(f"Error calculating return period: {e}")
            return None

    @staticmethod
    async def get_major_floods_by_decade(
        db: AsyncSession,
        min_severity: str = 'major'
    ) -> Dict[int, int]:
        """
        Get count of major floods by decade

        Args:
            db: Database session
            min_severity: Minimum severity level

        Returns:
            Dictionary mapping decade to flood count
        """
        try:
            query = select(HistoricalFlood).where(
                or_(
                    HistoricalFlood.severity == 'major',
                    HistoricalFlood.severity == 'catastrophic'
                )
            )

            result = await db.execute(query)
            floods = result.scalars().all()

            # Group by decade
            by_decade = {}
            for flood in floods:
                decade = (flood.event_date.year // 10) * 10
                by_decade[decade] = by_decade.get(decade, 0) + 1

            return dict(sorted(by_decade.items()))

        except Exception as e:
            logger.error(f"Error getting floods by decade: {e}")
            raise DatabaseError(f"Failed to get floods by decade: {str(e)}")