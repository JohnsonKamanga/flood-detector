"""
Open-Meteo Weather Service
Free, open-source weather API with global coverage
"""

import logging
import aiohttp
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenMeteoService:
    """Service for fetching weather data from Open-Meteo API"""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> Optional[Dict]:
        """
        Get weather forecast for a location
        
        Args:
            latitude: Latitude
            longitude: Longitude
            days: Number of days to forecast (1-16)
        
        Returns:
            Dictionary with forecast data or None if failed
        """
        try:
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'hourly': 'precipitation,precipitation_probability,temperature_2m,relative_humidity_2m',
                'daily': 'precipitation_sum,precipitation_probability_max',
                'forecast_days': min(days, 16),
                'timezone': 'auto'
            }
            
            async with self.session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_forecast(data)
                else:
                    logger.error(f"Open-Meteo API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Open-Meteo forecast: {e}")
            return None
    
    def _format_forecast(self, data: Dict) -> Dict:
        """
        Format Open-Meteo response to match NOAA format
        
        Args:
            data: Raw Open-Meteo response
        
        Returns:
            Formatted forecast data
        """
        try:
            hourly = data.get('hourly', {})
            daily = data.get('daily', {})
            
            # Convert hourly data to periods (similar to NOAA format)
            periods = []
            times = hourly.get('time', [])
            precip = hourly.get('precipitation', [])
            precip_prob = hourly.get('precipitation_probability', [])
            temp = hourly.get('temperature_2m', [])
            humidity = hourly.get('relative_humidity_2m', [])
            
            # Group into 3-hour periods (8 periods per day)
            for i in range(0, min(len(times), 56), 3):  # 7 days * 8 periods
                if i < len(times):
                    period = {
                        'name': f"Period {i//3 + 1}",
                        'startTime': times[i],
                        'temperature': temp[i] if i < len(temp) else None,
                        'precipitation_probability': precip_prob[i] if i < len(precip_prob) else 0,
                        'precipitation_amount': sum(precip[i:i+3]) if i+3 <= len(precip) else 0,
                        'relative_humidity': humidity[i] if i < len(humidity) else None,
                        'isDaytime': self._is_daytime(times[i])
                    }
                    periods.append(period)
            
            return {
                'periods': periods,
                'daily_precipitation': daily.get('precipitation_sum', []),
                'daily_precipitation_probability': daily.get('precipitation_probability_max', []),
                'source': 'open-meteo',
                'location': {
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'timezone': data.get('timezone')
                }
            }
            
        except Exception as e:
            logger.error(f"Error formatting Open-Meteo data: {e}")
            return {'periods': []}
    
    def _is_daytime(self, time_str: str) -> bool:
        """Determine if time is daytime (6 AM - 6 PM)"""
        try:
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            hour = dt.hour
            return 6 <= hour < 18
        except:
            return True


async def get_weather_forecast(
    latitude: float,
    longitude: float,
    prefer_noaa: bool = True
) -> Optional[Dict]:
    """
    Get weather forecast with fallback support
    
    Tries NOAA first (US only), falls back to Open-Meteo (global)
    
    Args:
        latitude: Latitude
        longitude: Longitude
        prefer_noaa: Whether to try NOAA first (for US locations)
    
    Returns:
        Weather forecast data or None
    """
    forecast = None
    
    # Try NOAA first if preferred (US locations)
    if prefer_noaa:
        try:
            from app.services.noaa_service import NOAAService
            async with NOAAService() as noaa:
                forecast = await noaa.get_forecast_by_point(latitude, longitude)
                if forecast:
                    logger.debug(f"Using NOAA forecast for ({latitude}, {longitude})")
                    return forecast
        except Exception as e:
            logger.debug(f"NOAA unavailable, trying Open-Meteo: {e}")
    
    # Fallback to Open-Meteo (global coverage)
    try:
        async with OpenMeteoService() as meteo:
            forecast = await meteo.get_forecast(latitude, longitude)
            if forecast:
                logger.info(f"Using Open-Meteo forecast for ({latitude}, {longitude})")
                return forecast
    except Exception as e:
        logger.error(f"Open-Meteo also failed: {e}")
    
    return None
