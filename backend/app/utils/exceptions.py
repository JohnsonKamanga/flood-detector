"""
Custom exception classes for the application
"""

from typing import Any, Dict, Optional


class FloodPredictionException(Exception):
    """Base exception for flood prediction system"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DataValidationError(FloodPredictionException):
    """Raised when data validation fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class ExternalAPIError(FloodPredictionException):
    """Raised when external API calls fail"""

    def __init__(
        self,
        message: str,
        api_name: str,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details['api_name'] = api_name
        super().__init__(message, status_code=502, details=details)


class DatabaseError(FloodPredictionException):
    """Raised when database operations fail"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class ResourceNotFoundError(FloodPredictionException):
    """Raised when a requested resource is not found"""

    def __init__(self, resource_type: str, resource_id: Any):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, status_code=404, details={
            'resource_type': resource_type,
            'resource_id': resource_id
        })


class AuthenticationError(FloodPredictionException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(FloodPredictionException):
    """Raised when authorization fails"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class RateLimitError(FloodPredictionException):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class SpatialProcessingError(FloodPredictionException):
    """Raised when spatial processing fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class PredictionError(FloodPredictionException):
    """Raised when flood prediction fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)