import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

class NOAAService:
    """Service for fetching weather data from NOAA API"""

    def __init__(self):
        self.base_url = settings.noaa_api_base_url
        self.token = settings.noaa_api_token
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        headers = {
            'User-Agent': 'FloodPredictionSystem/1.0',
        }
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_forecast_by_point(self, latitude: float, longitude: float) -> Dict:
        """
        Get weather forecast for a specific point

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Forecast data including precipitation
        """
        try:
            # First, get the forecast grid endpoint
            points_url = f"{self.base_url}/points/{latitude},{longitude}"
            async with self.session.get(points_url) as response:
                response.raise_for_status()
                points_data = await response.json()

            # Get the forecast URL
            forecast_url = points_data['properties']['forecast']

            # Fetch the forecast
            async with self.session.get(forecast_url) as response:
                response.raise_for_status()
                forecast_data = await response.json()

            return self._parse_forecast(forecast_data)

        except aiohttp.ClientError as e:
            logger.error(f"Error fetching NOAA forecast: {e}")
            raise

    async def get_active_alerts(self, state: str = None) -> List[Dict]:
        """
        Get active weather alerts

        Args:
            state: Two-letter state code (optional)

        Returns:
            List of active alerts
        """
        url = f"{self.base_url}/alerts/active"
        params = {}

        if state:
            params['area'] = state

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return self._parse_alerts(data)

        except aiohttp.ClientError as e:
            logger.error(f"Error fetching NOAA alerts: {e}")
            raise

    async def get_precipitation_data(
        self, 
        latitude: float, 
        longitude: float,
        hours: int = 24
    ) -> Dict:
        """
        Get precipitation data for a location

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            hours: Number of hours to look back

        Returns:
            Precipitation data
        """
        try:
            # Get observation stations near the point
            stations_url = f"{self.base_url}/points/{latitude},{longitude}/stations"
            async with self.session.get(stations_url) as response:
                response.raise_for_status()
                stations_data = await response.json()

            # Get the nearest station
            if not stations_data.get('features'):
                logger.warning(f"No stations found near {latitude}, {longitude}")
                return {}

            station_id = stations_data['features'][0]['properties']['stationIdentifier']

            # Get observations from the station
            observations_url = f"{self.base_url}/stations/{station_id}/observations"
            params = {'limit': hours}

            async with self.session.get(observations_url, params=params) as response:
                response.raise_for_status()
                observations_data = await response.json()

            return self._parse_precipitation(observations_data)

        except aiohttp.ClientError as e:
            logger.error(f"Error fetching precipitation data: {e}")
            raise

    def _parse_forecast(self, data: Dict) -> Dict:
        """Parse NOAA forecast response"""
        try:
            periods = data.get('properties', {}).get('periods', [])

            parsed_forecast = {
                'updated': data.get('properties', {}).get('updated'),
                'periods': []
            }

            for period in periods:
                parsed_forecast['periods'].append({
                    'name': period.get('name'),
                    'start_time': period.get('startTime'),
                    'end_time': period.get('endTime'),
                    'temperature': period.get('temperature'),
                    'temperature_unit': period.get('temperatureUnit'),
                    'precipitation_probability': period.get('probabilityOfPrecipitation', {}).get('value'),
                    'detailed_forecast': period.get('detailedForecast'),
                    'short_forecast': period.get('shortForecast')
                })

            return parsed_forecast

        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing forecast: {e}")
            return {}

    def _parse_alerts(self, data: Dict) -> List[Dict]:
        """Parse NOAA alerts response"""
        try:
            features = data.get('features', [])
            alerts = []

            for feature in features:
                props = feature.get('properties', {})

                # Filter for flood-related alerts
                event_type = props.get('event', '').lower()
                if any(keyword in event_type for keyword in ['flood', 'flash', 'water', 'rain']):
                    alerts.append({
                        'id': props.get('id'),
                        'event': props.get('event'),
                        'severity': props.get('severity'),
                        'certainty': props.get('certainty'),
                        'urgency': props.get('urgency'),
                        'headline': props.get('headline'),
                        'description': props.get('description'),
                        'instruction': props.get('instruction'),
                        'area_desc': props.get('areaDesc'),
                        'effective': props.get('effective'),
                        'expires': props.get('expires'),
                        'geometry': feature.get('geometry')
                    })

            return alerts

        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing alerts: {e}")
            return []

    def _parse_precipitation(self, data: Dict) -> Dict:
        """Parse precipitation observations"""
        try:
            features = data.get('features', [])

            total_precipitation = 0
            observations = []

            for feature in features:
                props = feature.get('properties', {})

                precip = props.get('precipitationLastHour', {}).get('value')
                if precip:
                    # Convert from mm to inches
                    precip_inches = precip * 0.0393701
                    total_precipitation += precip_inches

                observations.append({
                    'timestamp': props.get('timestamp'),
                    'temperature': props.get('temperature', {}).get('value'),
                    'precipitation_in': precip_inches if precip else 0,
                    'humidity': props.get('relativeHumidity', {}).get('value'),
                    'wind_speed': props.get('windSpeed', {}).get('value')
                })

            return {
                'total_precipitation_in': total_precipitation,
                'observations': observations
            }

        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing precipitation: {e}")
            return {}