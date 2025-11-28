
import React, { useState, useEffect } from 'react';
import FloodMap from '@/components/Map/FloodMap';
import AlertPanel from './AlertPanel';
import GaugeList from './GaugeList';
import RiskSummary from './RiskSummary';
import { useFloodData } from '@/hooks/useFloodData';
import { useWebSocket } from '@/hooks/useWebSocket';
import { apiService } from '@/services/api';
import type { GaugeData, HeatmapData } from '@/types/flood.types';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import ErrorMessage from '@/components/shared/ErrorMessage';

const Dashboard: React.FC = () => {
    const { gauges, predictions, loading, error, refetch } = useFloodData();
    const { connected, onMessage } = useWebSocket();
    const [selectedGauge, setSelectedGauge] = useState<GaugeData | null>(null);
    const [showHeatmap, setShowHeatmap] = useState(false);
    const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
  
    // Handle WebSocket updates
    useEffect(() => {
      const unsubscribe = onMessage('gauge_update', (data) => {
        console.log('Gauge update received:', data);
        refetch();
      });
  
      return unsubscribe;
    }, [onMessage, refetch]);

    // Fetch heatmap data
    const loadHeatmap = async () => {
      if (gauges.length === 0) return;

      const lats = gauges.map((g) => g.latitude);
      const lons = gauges.map((g) => g.longitude);

      const minLat = Math.min(...lats);
      const maxLat = Math.max(...lats);
      const minLon = Math.min(...lons);
      const maxLon = Math.max(...lons);

      const bbox = `${minLon},${minLat},${maxLon},${maxLat}`;

      try {
        const data = await apiService.getRiskHeatmap(bbox);
        setHeatmapData(data);
      } catch (err) {
        console.error('Error loading heatmap:', err);
      }
    };

    useEffect(() => {
        if (showHeatmap) {
          loadHeatmap();
        }
      }, [showHeatmap, gauges]);
    
    if (loading && gauges.length === 0) {
        return (
          <div className="flex items-center justify-center h-screen">
            <LoadingSpinner />
          </div>
        );
      }
    
    if (error) {
        return (
          <div className="flex items-center justify-center h-screen">
            <ErrorMessage message={error} onRetry={refetch} />
          </div>
        );
      }
    
    const highRiskGauges = gauges.filter(
        (g) => g.current_stage === 'flood' || g.current_stage === 'major'
      );
    