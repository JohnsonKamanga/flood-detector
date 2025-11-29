import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';
import type { GaugeData, FloodPrediction } from '@/types/flood.types';

export function useFloodData(refreshInterval: number = 300000) { // 5 minutes
  const [gauges, setGauges] = useState<GaugeData[]>([]);
  const [predictions, setPredictions] = useState<FloodPrediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [gaugesData, predictionsData] = await Promise.all([
        apiService.getGauges(),
        apiService.getPredictions({ hours: 24 }),
      ]);

      setGauges(gaugesData);
      setPredictions(predictionsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
      console.error('Error fetching flood data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    const interval = setInterval(fetchData, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  return { gauges, predictions, loading, error, refetch: fetchData };
}
