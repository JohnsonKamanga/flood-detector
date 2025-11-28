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
        
        {/* Filter buttons */}
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
