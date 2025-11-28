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
  