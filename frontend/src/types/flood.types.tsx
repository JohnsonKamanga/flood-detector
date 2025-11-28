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
  