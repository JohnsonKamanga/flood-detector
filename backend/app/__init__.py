"""
Urban Flood Prediction System - Backend Application
Main application package initialization
"""

__version__ = "1.0.0"
__author__ = "Flood Prediction Team"
__description__ = "Real-time flood prediction and monitoring system"

from app.config import settings

# Application metadata
APP_NAME = "Flood Prediction API"
APP_VERSION = __version__
API_PREFIX = "/api"

# Export commonly used items
__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "API_PREFIX",
    "settings",
]