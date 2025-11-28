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