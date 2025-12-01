import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import { divIcon } from 'leaflet';
import { renderToStaticMarkup } from 'react-dom/server';
import type { GaugeData } from '@/types/flood.types';
import { formatDistanceToNow } from 'date-fns';

interface GaugeMarkerProps {
  gauge: GaugeData;
  onClick?: () => void;
}

const getStageColor = (stage: string | null): string => {
  switch (stage) {
    case 'major':
      return 'bg-red-500';
    case 'flood':
      return 'bg-orange-500';
    case 'action':
      return 'bg-yellow-500';
    case 'normal':
    default:
      return 'bg-green-500';
  }
};

const GaugeMarker: React.FC<GaugeMarkerProps> = ({ gauge, onClick }) => {
  const stageColor = getStageColor(gauge.current_stage);

  const icon = divIcon({
    html: renderToStaticMarkup(
      <div className={`${stageColor} w-6 h-6 rounded-full border-2 border-white shadow-lg`}>
        <div className="w-full h-full rounded-full animate-ping opacity-75"></div>
      </div>
    ),
    className: '',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });

  return (
    <Marker
      position={[gauge.latitude, gauge.longitude]}
      icon={icon}
      eventHandlers={{
        click: onClick,
      }}
    >
      <Popup>
        <div className="p-2 min-w-[200px]">
          <h3 className="font-semibold text-lg mb-2">{gauge.name}</h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Site ID:</span>
              <span className="font-medium">{gauge.usgs_site_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Stage:</span>
              <span className={`font-medium capitalize ${stageColor.replace('bg-', 'text-')}`}>
                {gauge.current_stage || 'Unknown'}
              </span>
            </div>
            {gauge.current_gauge_height_ft !== null && (
              <div className="flex justify-between">
                <span className="text-gray-600">Height:</span>
                <span className="font-medium">{gauge.current_gauge_height_ft.toFixed(2)} ft</span>
              </div>
            )}
            {gauge.current_flow_cfs !== null && (
              <div className="flex justify-between">
                <span className="text-gray-600">Flow:</span>
                <span className="font-medium">{gauge.current_flow_cfs.toFixed(0)} cfs</span>
              </div>
            )}
            <div className="flex justify-between text-xs text-gray-500 pt-2">
              <span>Updated:</span>
              <span>{formatDistanceToNow(new Date(gauge.last_updated), { addSuffix: true })}</span>
            </div>
          </div>
        </div>
      </Popup>
    </Marker>
  );
};

export default GaugeMarker;