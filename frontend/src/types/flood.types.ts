export interface GaugeData {
    id: number;
    usgs_site_id: string;
    name: string;
    latitude: number;
    longitude: number;
    current_flow_cfs: number | null;
    current_gauge_height_ft: number | null;
    current_stage: 'normal' | 'action' | 'flood' | 'major' | null;
    last_updated: string;
    elevation_ft?: number;
    action_stage_ft?: number;
    flood_stage_ft?: number;
    major_flood_stage_ft?: number;
  }

export interface GaugeMeasurement {
    id: number;
    timestamp: string;
    flow_cfs: number | null;
    gauge_height_ft: number | null;
    precipitation_in: number | null;
  }

export interface FloodPrediction {
    id: number;
    prediction_time: string;
    valid_time: string;
    risk_level: 'low' | 'moderate' | 'high' | 'severe';
    risk_score: number;
    confidence: number | null;
    rainfall_forecast_in: number | null;
    affected_gauges: { gauge_ids: number[] } | null;
  }
  
export interface RiskZone {
    id: number;
    zone_name: string;
    base_risk_level: string;
    population_estimate: number | null;
    elevation_avg_ft: number | null;
  }

export interface HeatmapData {
    bounds: {
      min_lon: number;
      min_lat: number;
      max_lon: number;
      max_lat: number;
    };
    resolution: number;
    heatmap: {
      longitude: number[];
      latitude: number[];
      risk_values: number[][];
    };
    gauge_count: number;
    timestamp: string;
  }
  
export interface WebSocketMessage {
    type: 'connection' | 'gauge_update' | 'risk_alert' | 'prediction_update' | 'error' | 'pong';
    status?: string;
    message?: string;
    data?: any;
    severity?: string;
    timestamp?: string;
  }  