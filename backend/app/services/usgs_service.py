import aiohttp
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)

class USGSService:
    """Service for fetching data from USGS Water Service API"""

    def __init__(self):
        self.base_url = settings.usgs_api_base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_site_data(self, site_codes: List[str], parameters: List[str] = None) -> Dict:
        """
        Fetch current data for specified USGS sites

        Args:
            site_codes: List of USGS site codes (e.g., ['01646500', '01589300'])
            parameters: List of parameter codes (e.g., ['00060', '00065'])
                       00060 = Discharge (cfs)
                       00065 = Gage height (ft)

        Returns:
            Dictionary containing site data
        """
        if parameters is None:
            parameters = ['00060', '00065']

        params = {
            'format': 'json',
            'sites': ','.join(site_codes),
            'parameterCd': ','.join(parameters),
            'siteStatus': 'active'
        }

        try:
            async with self.session.get(self.base_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return self._parse_usgs_response(data)
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching data from USGS API: {e}")
            return None

    async def get_historical_data(self, site_code: str, start_date: str, end_date: str, parameters: List[str] = None) -> Dict:
        """Fetch historical data for a site"""
        if parameters is None:
            parameters = ['00060', '00065']

        params = {
            'format': 'json',
            'sites': site_code,
            'parameterCd': ','.join(parameters),
            'startDT': start_date.isoformat(),
            'endDT': end_date.isoformat()
        }
        
        try:
            async with self.session.get(self.base_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return self._parse_usgs_response(data)
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching historical data from USGS API: {e}")
            raise
    
    def _parse_usgs_response(self, data: Dict) -> Dict:
        """Parse USGS API response into structured format"""
        parsed_data = {}

        try:
            time_series = data.get('value', {}).get('timeSeries', [])
            
            for series in time_series:
                site_code = series['sourceInfo']['siteCode'][0]['value']
                variable_name = series['variable']['variableName']
                variable_code = series['variable']['variableCode'][0]['value']

                values = series.get('values', [{}])[0].get('value', [])

                if site_code not in parsed_data:
                    parsed_data[site_code] = {
                        'site_name': series['sourceInfo']['siteName'],
                        'latitude': float(series['sourceInfo']['geoLocation']['geogLocation']['latitude']),
                        'longitude': float(series['sourceInfo']['geoLocation']['geogLocation']['longitude']),
                        'measurements': []
                    }
                
                for value_obj in values:
                    timestamp = datetime.fromisoformat(value_obj['dateTime'].replace('Z', '+00:00'))
                    value = float(value_obj['value'])


                    parsed_data[site_code]['measurements'].append({
                        'timestamp': timestamp,
                        'parameter': variable_code,
                        'parameter_name': variable_name,
                        'value': value,
                        'qualifiers': value_obj.get('qualifiers', [])
                    })
            return parsed_data
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Error parsing USGS response: {e}")
            return {}
    
    async def get_site_by_bounds(self, bbox: tuple, parameter_codes: List[str] = None) -> Dict:
        """
        Get active sites within a bounding box

        Args:
            bbox: (min_lon, min_lat, max_lon, max_lat)
            parameter_codes: Optional list of parameter codes to filter
        """
        params = {
            'format': 'json',
            'bbox': ','.join(map(str, bbox)),
            'siteStatus': 'active',
            'siteType': 'ST', #stream
            'hasDataTypeCd': 'iv' #instantaneous value
        }

        if parameter_codes:
            params['parameterCd'] = ','.join(parameter_codes)
        
        url = self.base_url.replace('/iv', '/site')

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return self._parse_site_list(data)
        
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching sites by bounds: {e}")
            raise
        
    def _parse_site_list(self, data: Dict) -> Dict:
        """Parse site list response"""
        sites = []

        try:
            site_list = data.get('value', {}).get('timeSeries', [])
            for site_data in site_list:
                source_info = site_data.get('sourceInfo', {})
                geo_location = source_info.get('geoLocation', {}).get('geogLocation', {})
                
                sites.append({
                    'site_code': source_info['siteCode'][0]['value'],
                    'site_name': source_info.get('siteName', 'Unknown'),
                    'latitude': float(geo_location.get('latitude', 0)),
                    'longitude': float(geo_location.get('longitude', 0)),
                    'site_type': source_info.get('siteType', {}).get('siteTypeName', 'Unknown')
                })
            return sites
            
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Error parsing site list: {e}")
            return {}
