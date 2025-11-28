import { LatLngExpression } from 'leaflet';

export interface MapBounds {
  minLon: number;
  minLat: number;
  maxLon: number;
  maxLat: number;
}

export interface MarkerData {
    position: LatLngExpression;
    id: number;
    name: string;
    stage: string | null;
    data: any;
  }

export interface HeatmapLayer {
    data: number[][];
    bounds: [[number, number], [number, number]];
    gradient: Record<number, string>;
  }
   