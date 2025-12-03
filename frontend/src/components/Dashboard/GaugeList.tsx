import React, { useState } from 'react';
import type { GaugeData } from '@/types/flood.types';
import { formatDistanceToNow } from 'date-fns';

interface GaugeListProps {
  gauges: GaugeData[];
  selectedGauge: GaugeData | null;
  onGaugeSelect?: (gauge: GaugeData) => void;
}

const GaugeList: React.FC<GaugeListProps> = ({ gauges, selectedGauge, onGaugeSelect }) => {
  const [filter, setFilter] = useState<string>('all');

  const filteredGauges = gauges.filter((gauge) => {
    if (filter === 'all') return true;
    return gauge.current_stage === filter;
  });

  const getStageColor = (stage: string | null): string => {
    switch (stage) {
      case 'major':
        return 'text-red-600 bg-red-50';
      case 'flood':
        return 'text-orange-600 bg-orange-50';
      case 'action':
        return 'text-yellow-600 bg-yellow-50';
      case 'normal':
      default:
        return 'text-green-600 bg-green-50';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold mb-3">River Gauges</h2>
        
        
        <div className="flex gap-2 flex-wrap">
          {['all', 'major', 'flood', 'action', 'normal'].map((stage) => (
            <button
              key={stage}
              onClick={() => setFilter(stage)}
              className={`px-3 py-1 rounded text-sm font-medium transition ${
                filter === stage
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {stage.charAt(0).toUpperCase() + stage.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="max-h-96 overflow-y-auto">
        {filteredGauges.length === 0 ? (
          <div className="p-4 text-center text-gray-500">No gauges found</div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredGauges.map((gauge) => (
              <button
                key={gauge.id}
                onClick={() => onGaugeSelect?.(gauge)}
                className={`w-full text-left p-4 hover:bg-gray-50 transition ${
                  selectedGauge?.id === gauge.id ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{gauge.name}</h3>
                    <p className="text-sm text-gray-500">{gauge.usgs_site_id}</p>
                  </div>
                  <span
                    className={`px-2 py-1 rounded text-xs font-semibold ${getStageColor(
                      gauge.current_stage
                    )}`}
                  >
                    {gauge.current_stage?.toUpperCase() || 'N/A'}
                  </span>
                </div>

                <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                  {gauge.current_gauge_height_ft !== null && (
                    <div>
                      <span className="text-gray-600">Height:</span>
                      <span className="ml-1 font-medium">
                        {gauge.current_gauge_height_ft.toFixed(2)} ft
                      </span>
                    </div>
                  )}
                  {gauge.current_flow_cfs !== null && (
                    <div>
                      <span className="text-gray-600">Flow:</span>
                      <span className="ml-1 font-medium">
                        {gauge.current_flow_cfs.toFixed(0)} cfs
                      </span>
                    </div>
                  )}
                </div>

                <div className="mt-2 text-xs text-gray-500">
                  Updated {formatDistanceToNow(new Date(gauge.last_updated), { addSuffix: true })}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GaugeList;
