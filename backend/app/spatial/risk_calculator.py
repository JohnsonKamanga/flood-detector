import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from app.spatial.simple_processor import SimpleSpatialProcessor

logger = logging.getLogger(__name__)

class FloodRiskCalculator:
    """Calculate flood risk based on multiple factors"""
    
    RISK_THRESHOLDS = {
        'low': (0, 25),
        'moderate': (25, 50),
        'high': (50, 75),
        'severe': (75, 100)
    }
    
    def __init__(self):
        self.weights = {
            'gauge_height': 0.40,
            'rainfall': 0.30,
            'soil_saturation': 0.20,
            'proximity': 0.10
        }
        self.spatial_processor = SimpleSpatialProcessor()
    
    def calculate_composite_risk(
        self,
        gauge_data: List[Dict],
        rainfall_forecast: Dict,
        soil_moisture: float,
        location: Optional[Tuple[float, float]] = None
    ) -> Dict:
        """
        Calculate composite flood risk score
        
        Args:
            gauge_data: List of gauge measurements
            rainfall_forecast: Precipitation forecast data
            soil_moisture: Soil saturation percentage (0-100)
            location: Optional (longitude, latitude) for location-specific risk
        
        Returns:
            Risk assessment dictionary
        """
        # Calculate individual risk components
        gauge_risk = self._calculate_gauge_risk(gauge_data)
        rainfall_risk = self._calculate_rainfall_risk(rainfall_forecast)
        saturation_risk = self._calculate_saturation_risk(soil_moisture)
        
        # Calculate proximity risk if location provided
        proximity_risk = 0.0
        if location and gauge_data:
            gauge_locations = [
                (g.get('longitude', 0), g.get('latitude', 0))
                for g in gauge_data
                if 'longitude' in g and 'latitude' in g
            ]
            if gauge_locations:
                proximity_scores = self.spatial_processor.calculate_proximity_scores(
                    [location],
                    gauge_locations,
                    max_distance=5000.0
                )
                proximity_risk = proximity_scores[0] if proximity_scores else 0.0
        
        # Composite score
        composite_score = (
            gauge_risk * self.weights['gauge_height'] +
            rainfall_risk * self.weights['rainfall'] +
            saturation_risk * self.weights['soil_saturation'] +
            proximity_risk * self.weights['proximity']
        )
        
        # Determine risk level
        risk_level = self._get_risk_level(composite_score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(gauge_data, rainfall_forecast)
        
        return {
            'composite_score': round(composite_score, 2),
            'risk_level': risk_level,
            'confidence': round(confidence, 2),
            'components': {
                'gauge_risk': round(gauge_risk, 2),
                'rainfall_risk': round(rainfall_risk, 2),
                'saturation_risk': round(saturation_risk, 2),
                'proximity_risk': round(proximity_risk, 2)
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_gauge_risk(self, gauge_data: List[Dict]) -> float:
        """Calculate risk from gauge measurements"""
        if not gauge_data:
            return 0
        
        risk_scores = []
        
        for gauge in gauge_data:
            current_height = gauge.get('current_gauge_height_ft', 0)
            flood_stage = gauge.get('flood_stage_ft', 999)
            action_stage = gauge.get('action_stage_ft', 999)
            
            if current_height >= flood_stage:
                score = 100
            elif current_height >= action_stage:
                score = 50 + ((current_height - action_stage) / 
                             (flood_stage - action_stage)) * 50
            else:
                score = (current_height / action_stage) * 50
            
            risk_scores.append(min(score, 100))
        
        return max(risk_scores) if risk_scores else 0
    
    def _calculate_rainfall_risk(self, rainfall_forecast: Dict) -> float:
        """Calculate risk from rainfall forecast"""
        if not rainfall_forecast:
            return 0
        
        periods = rainfall_forecast.get('periods', [])
        
        total_rainfall = 0
        for period in periods[:8]:
            prob = period.get('precipitation_probability', 0) or 0
            estimated_amount = (prob / 100) * 0.5
            total_rainfall += estimated_amount
        
        if total_rainfall >= 6:
            return 100
        elif total_rainfall >= 4:
            return 75
        elif total_rainfall >= 2:
            return 50
        elif total_rainfall >= 1:
            return 25
        else:
            return (total_rainfall / 1) * 25
    
    def _calculate_saturation_risk(self, soil_moisture: float) -> float:
        """Calculate risk from soil saturation"""
        if soil_moisture >= 90:
            return 100
        elif soil_moisture >= 75:
            return 75
        elif soil_moisture >= 50:
            return 50
        else:
            return (soil_moisture / 50) * 50
    
    def _get_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level"""
        for level, (min_score, max_score) in self.RISK_THRESHOLDS.items():
            if min_score <= score < max_score:
                return level
        return 'severe'
    
    def _calculate_confidence(
        self, 
        gauge_data: List[Dict], 
        rainfall_forecast: Dict
    ) -> float:
        """Calculate confidence in risk assessment"""
        confidence = 1.0
        
        if not gauge_data:
            confidence *= 0.5
        
        if not rainfall_forecast:
            confidence *= 0.7
        
        for gauge in gauge_data:
            last_updated = gauge.get('last_updated')
            if last_updated:
                if isinstance(last_updated, str):
                    last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                age_hours = (datetime.utcnow() - last_updated).total_seconds() / 3600
                if age_hours > 24:
                    confidence *= 0.8
        
        return max(confidence, 0.1)
    
    def generate_risk_zones(
        self,
        gauge_locations: List[Tuple[float, float]],
        risk_scores: List[float],
        grid_resolution: int = 100
    ) -> Dict:
        """Generate spatial risk zones using interpolation"""
        result = self.spatial_processor.interpolate_values(
            gauge_locations,
            risk_scores,
            grid_resolution
        )
        
        if result:
            return {
                'longitude': result['longitude'],
                'latitude': result['latitude'],
                'risk_values': result['values']
            }
        
        return {}