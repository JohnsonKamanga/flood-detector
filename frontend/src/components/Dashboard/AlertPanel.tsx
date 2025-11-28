import React from 'react';
import type { GaugeData } from '@/types/flood.types';
import { formatDistanceToNow } from 'date-fns';

interface AlertPanelProps {
  gauges: GaugeData[];
  onGaugeClick?: (gauge: GaugeData) => void;
}

const AlertPanel: React.FC<AlertPanelProps> = ({ gauges, onGaugeClick }) => {
  if (gauges.length === 0) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-bold">!</span>
        </div>
        <h2 className="text-lg font-semibold text-red-900">Active Flood Alerts</h2>
      </div>

      <div className="space-y-2">
        {gauges.map((gauge) => (
          <button
            key={gauge.id}
            onClick={() => onGaugeClick?.(gauge)}
            className="w-full text-left p-3 bg-white rounded border border-red-300 hover:border-red-400 transition"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-gray-900">{gauge.name}</h3>
                <p className="text-sm text-gray-600">{gauge.usgs_site_id}</p>
              </div>
              <span
                className={`px-2 py-1 rounded text-xs font-semibold ${
                  gauge.current_stage === 'major'
                    ? 'bg-red-500 text-white'
                    : 'bg-orange-500 text-white'
                }`}
              >
                {gauge.current_stage?.toUpperCase()}
              </span>
            </div>
            <div className="mt-2 text-sm text-gray-600">
              {gauge.current_gauge_height_ft && (
                <span>Height: {gauge.current_gauge_height_ft.toFixed(2)} ft</span>
              )}
              <span className="mx-2">•</span>
              <span>{formatDistanceToNow(new Date(gauge.last_updated), { addSuffix: true })}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default AlertPanel;