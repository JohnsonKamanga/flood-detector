"""
API routes package
"""

from app.routes import gauges, predictions, websocket, historical

__all__ = [
    "gauges",
    "predictions", 
    "websocket",
    "historical",  # Add this
]