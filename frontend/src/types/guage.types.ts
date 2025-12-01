export interface GaugeThresholds {
  action_stage_ft: number | null;
  flood_stage_ft: number | null;
  major_flood_stage_ft: number | null;
}

export interface GaugeLocation {
  latitude: number;
  longitude: number;
  elevation_ft: number | null;
}

export interface GaugeStatus {
  current_stage: 'normal' | 'action' | 'flood' | 'major' | null;
  current_flow_cfs: number | null;
  current_gauge_height_ft: number | null;
  last_updated: string;
}

export interface GaugeMetadata {
  id: number;
  usgs_site_id: string;
  name: string;
  drainage_area_sqmi: number | null;
  is_active: boolean;
  created_at: string;
}

export interface Gauge extends GaugeMetadata, GaugeLocation, GaugeStatus, GaugeThresholds {}

export interface GaugeMeasurementPoint {
  timestamp: string;
  flow_cfs: number | null;
  gauge_height_ft: number | null;
  precipitation_in: number | null;
  temperature_f: number | null;
}

export interface GaugeHistory {
  gauge_id: number;
  measurements: GaugeMeasurementPoint[];
  period_hours: number;
}

export interface GaugeAlert {
  gauge_id: number;
  gauge_name: string;
  severity: 'action' | 'flood' | 'major';
  current_height: number;
  threshold_height: number;
  message: string;
  timestamp: string;
}

export interface GaugeFilter {
  stage?: 'normal' | 'action' | 'flood' | 'major';
  search?: string;
  withinBounds?: {
    minLat: number;
    maxLat: number;
    minLon: number;
    maxLon: number;
  };
  sortBy?: 'name' | 'height' | 'stage' | 'updated';
  sortOrder?: 'asc' | 'desc';
}
