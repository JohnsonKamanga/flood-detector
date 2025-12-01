
import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import { LatLngBounds } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import GaugeMarker from './GuageMarker';
import RiskHeatmap from './RiskHeatmap';
import type { GaugeData, HeatmapData } from '@/types/flood.types';

interface FloodMapProps {
  gauges: GaugeData[];
  center?: [number, number];
  zoom?: number;
  showHeatmap?: boolean;
  heatmapData?: HeatmapData | null;
  onGaugeClick?: (gauge: GaugeData) => void;
}

const MapController: React.FC<{ bounds?: LatLngBounds }> = ({ bounds }) => {
  const map = useMap();

  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds);
    }
  }, [bounds, map]);

  return null;
};

const FloodMap: React.FC<FloodMapProps> = ({
  gauges,
  center = [38.9072, -77.0369], // Default: Washington DC
  zoom = 8,
  showHeatmap = false,
  heatmapData,
  onGaugeClick,
}) => {
  const [bounds, setBounds] = useState<LatLngBounds | undefined>();

  useEffect(() => {
    if (gauges.length > 0) {
      const latLngs = gauges.map((g) => [g.latitude, g.longitude] as [number, number]);
      const newBounds = new LatLngBounds(latLngs);
      setBounds(newBounds);
    }
  }, [gauges]);

  return (
    <div className="h-full w-full relative">
      <MapContainer
        center={center}
        zoom={zoom}
        className="h-full w-full"
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapController bounds={bounds} />

        {showHeatmap && heatmapData && <RiskHeatmap data={heatmapData} />}

        {gauges.map((gauge) => (
          <GaugeMarker
            key={gauge.id}
            gauge={gauge}
            onClick={() => onGaugeClick?.(gauge)}
          />
        ))}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white p-4 rounded-lg shadow-lg z-[1000]">
        <h3 className="font-semibold mb-2">Gauge Status</h3>
        <div className="space-y-1 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>Normal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
            <span>Action</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-orange-500"></div>
            <span>Flood</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500"></div>
            <span>Major</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FloodMap;

