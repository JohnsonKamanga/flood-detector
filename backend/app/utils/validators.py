"""
Data validation utilities
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from app.utils.exceptions import DataValidationError

logger = logging.getLogger(__name__)


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate geographic coordinates

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        True if valid

    Raises:
        DataValidationError: If coordinates are invalid
    """
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        raise DataValidationError("Coordinates must be numeric values")

    if not -90 <= latitude <= 90:
        raise DataValidationError(f"Latitude must be between -90 and 90, got {latitude}")

    if not -180 <= longitude <= 180:
        raise DataValidationError(f"Longitude must be between -180 and 180, got {longitude}")

    return True


def validate_gauge_data(data: Dict[str, Any]) -> bool:
    """
    Validate gauge data structure

    Args:
        data: Gauge data dictionary

    Returns:
        True if valid

    Raises:
        DataValidationError: If data is invalid
    """
    required_fields = ['usgs_site_id', 'name', 'latitude', 'longitude']

    for field in required_fields:
        if field not in data:
            raise DataValidationError(f"Missing required field: {field}")

    # Validate coordinates
    validate_coordinates(data['latitude'], data['longitude'])

    # Validate USGS site ID format (typically 8-15 digits)
    site_id = str(data['usgs_site_id'])
    if not site_id.isdigit() or not 8 <= len(site_id) <= 15:
        raise DataValidationError(f"Invalid USGS site ID format: {site_id}")

    # Validate numeric fields if present
    numeric_fields = ['current_flow_cfs', 'current_gauge_height_ft', 'elevation_ft']
    for field in numeric_fields:
        if field in data and data[field] is not None:
            if not isinstance(data[field], (int, float)):
                raise DataValidationError(f"{field} must be a numeric value")
            if data[field] < 0:
                raise DataValidationError(f"{field} cannot be negative")

    return True


def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    max_range_days: int = 365
) -> bool:
    """
    Validate a date range

    Args:
        start_date: Start datetime
        end_date: End datetime
        max_range_days: Maximum allowed range in days

    Returns:
        True if valid

    Raises:
        DataValidationError: If date range is invalid
    """
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        raise DataValidationError("Dates must be datetime objects")

    if start_date > end_date:
        raise DataValidationError("Start date must be before end date")

    range_days = (end_date - start_date).days
    if range_days > max_range_days:
        raise DataValidationError(
            f"Date range cannot exceed {max_range_days} days, got {range_days} days"
        )

    # Check if dates are not too far in the future
    max_future = datetime.utcnow() + timedelta(days=7)
    if end_date > max_future:
        raise DataValidationError("End date cannot be more than 7 days in the future")

    return True


def validate_risk_score(score: float) -> bool:
    """
    Validate risk score value

    Args:
        score: Risk score (0-100)

    Returns:
        True if valid

    Raises:
        DataValidationError: If score is invalid
    """
    if not isinstance(score, (int, float)):
        raise DataValidationError("Risk score must be a numeric value")

    if not 0 <= score <= 100:
        raise DataValidationError(f"Risk score must be between 0 and 100, got {score}")

    return True


def validate_radius(radius_km: float, max_radius: float = 100.0) -> bool:
    """
    Validate search radius

    Args:
        radius_km: Radius in kilometers
        max_radius: Maximum allowed radius

    Returns:
        True if valid

    Raises:
        DataValidationError: If radius is invalid
    """
    if not isinstance(radius_km, (int, float)):
        raise DataValidationError("Radius must be a numeric value")

    if radius_km <= 0:
        raise DataValidationError("Radius must be positive")

    if radius_km > max_radius:
        raise DataValidationError(f"Radius cannot exceed {max_radius} km")

    return True


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize string input

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        DataValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise DataValidationError("Value must be a string")

    # Remove potentially harmful characters
    sanitized = value.strip()

    # Check length
    if len(sanitized) > max_length:
        raise DataValidationError(f"String length cannot exceed {max_length} characters")

    # Basic XSS prevention
    dangerous_chars = ['<', '>', '"', "'", '\\']
    for char in dangerous_chars:
        if char in sanitized:
            sanitized = sanitized.replace(char, '')

    return sanitized


def validate_pagination(page: int, page_size: int, max_page_size: int = 100) -> bool:
    """
    Validate pagination parameters

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        max_page_size: Maximum allowed page size

    Returns:
        True if valid

    Raises:
        DataValidationError: If parameters are invalid
    """
    if not isinstance(page, int) or not isinstance(page_size, int):
        raise DataValidationError("Page and page_size must be integers")

    if page < 1:
        raise DataValidationError("Page must be >= 1")

    if page_size < 1:
        raise DataValidationError("Page size must be >= 1")

    if page_size > max_page_size:
        raise DataValidationError(f"Page size cannot exceed {max_page_size}")

    return True