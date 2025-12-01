import { useState, useCallback } from 'react';
import { LatLngBounds } from 'leaflet';

// interface MapControls {
//   center: [number, number];
//   zoom: number;
//   bounds: LatLngBounds | null;
// }

export function useMapControls(
  initialCenter: [number, number] = [38.9072, -77.0369],
  initialZoom: number = 8
) {
  const [center, setCenter] = useState<[number, number]>(initialCenter);
  const [zoom, setZoom] = useState<number>(initialZoom);
  const [bounds, setBounds] = useState<LatLngBounds | null>(null);

  const panTo = useCallback((newCenter: [number, number], newZoom?: number) => {
    setCenter(newCenter);
    if (newZoom !== undefined) {
      setZoom(newZoom);
    }
  }, []);

  const zoomIn = useCallback(() => {
    setZoom((prev) => Math.min(prev + 1, 18));
  }, []);

  const zoomOut = useCallback(() => {
    setZoom((prev) => Math.max(prev - 1, 1));
  }, []);

  const fitBounds = useCallback((newBounds: LatLngBounds) => {
    setBounds(newBounds);
  }, []);

  const reset = useCallback(() => {
    setCenter(initialCenter);
    setZoom(initialZoom);
    setBounds(null);
  }, [initialCenter, initialZoom]);

  return {
    center,
    zoom,
    bounds,
    panTo,
    zoomIn,
    zoomOut,
    fitBounds,
    reset,
  };
}
