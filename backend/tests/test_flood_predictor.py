# backend/tests/test_flood_predictor.py
import pytest
from app.spatial.risk_calculator import FloodRiskCalculator
from datetime import datetime

def test_gauge_risk_calculation():
    calculator = FloodRiskCalculator()

    gauge_data = [{
        'current_gauge_height_ft': 15.0,
        'flood_stage_ft': 20.0,
        'action_stage_ft': 12.0,
        'last_updated': datetime.utcnow()
    }]

    risk = calculator._calculate_gauge_risk(gauge_data)

    assert 0 <= risk <= 100
    assert risk > 50  # Above action stage

def test_rainfall_risk_calculation():
    calculator = FloodRiskCalculator()

    forecast = {
        'periods': [
            {'precipitation_probability': 80},
            {'precipitation_probability': 70},
            {'precipitation_probability': 60},
        ]
    }

    risk = calculator._calculate_rainfall_risk(forecast)

    assert 0 <= risk <= 100
    assert risk > 0

def test_composite_risk():
    calculator = FloodRiskCalculator()

    result = calculator.calculate_composite_risk(
        gauge_data=[{
            'current_gauge_height_ft': 15.0,
            'flood_stage_ft': 20.0,
            'action_stage_ft': 12.0,
            'last_updated': datetime.utcnow()
        }],
        rainfall_forecast={'periods': [{'precipitation_probability': 50}]},
        soil_moisture=60.0
    )

    assert 'composite_score' in result
    assert 'risk_level' in result
    assert 'confidence' in result
    assert result['risk_level'] in ['low', 'moderate', 'high', 'severe']