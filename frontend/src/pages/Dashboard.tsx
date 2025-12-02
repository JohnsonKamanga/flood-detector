import React, { useState, useEffect } from 'react';
import FloodMap from '@/components/map/FloodMap';
import AlertPanel from '@/components/Dashboard/AlertPanel';
import GaugeList from '@/components/Dashboard/GaugeList';
import RiskSummary from '@/components/Dashboard/RiskSummary';
import Header from '@/components/Layout/Header';
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
        <LoadingSpinner size="lg" message="Loading flood data..." fullScreen />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen p-4">
        <ErrorMessage
          message={error}
          title="Failed to Load Dashboard"
          onRetry={refetch}
        />
      </div>
    );
  }

  const highRiskGauges = gauges.filter(
    (g) => g.current_stage === 'flood' || g.current_stage === 'major'
  );

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header
        connected={connected}
        onToggleHeatmap={() => setShowHeatmap(!showHeatmap)}
        showHeatmap={showHeatmap}
      />

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-96 bg-white border-r border-gray-200 overflow-y-auto scrollbar-thin">
          <div className="p-4 space-y-4">
            <RiskSummary
              totalGauges={gauges.length}
              highRiskCount={highRiskGauges.length}
              predictions={predictions}
            />

            {highRiskGauges.length > 0 && (
              <AlertPanel gauges={highRiskGauges} onGaugeClick={setSelectedGauge} />
            )}

            <GaugeList
              gauges={gauges}
              selectedGauge={selectedGauge}
              onGaugeSelect={setSelectedGauge}
            />
          </div>
        </aside>

        <main className="flex-1">
          <FloodMap
            gauges={gauges}
            showHeatmap={showHeatmap}
            heatmapData={heatmapData}
            onGaugeClick={setSelectedGauge}
          />
        </main>
      </div>
    </div>
  );
};

export default Dashboard;