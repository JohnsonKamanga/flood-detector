import React, { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import type { HeatmapData } from '@/types/flood.types';

interface RiskHeatmapProps {
  data: HeatmapData;
}

const RiskHeatmap: React.FC<RiskHeatmapProps> = ({ data }) => {
  const map = useMap();

  useEffect(() => {
    if (!data.heatmap.risk_values.length) return;

    const { longitude, latitude, risk_values } = data.heatmap;
    const { min_lon, min_lat, max_lon, max_lat } = data.bounds;

    // Create canvas overlay
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = risk_values[0].length;
    const height = risk_values.length;

    canvas.width = width;
    canvas.height = height;

    // Color mapping for risk levels
    const getColor = (risk: number): [number, number, number, number] => {
      if (risk < 25) return [34, 197, 94, 128]; // Green
      if (risk < 50) return [234, 179, 8, 128]; // Yellow
      if (risk < 75) return [249, 115, 22, 128]; // Orange
      return [239, 68, 68, 192]; // Red
    };

    // Draw heatmap
    const imageData = ctx.createImageData(width, height);
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const risk = risk_values[y][x];
        const [r, g, b, a] = getColor(risk);
        const index = (y * width + x) * 4;
        
        imageData.data[index] = r;
        imageData.data[index + 1] = g;
        imageData.data[index + 2] = b;
        imageData.data[index + 3] = a;
      }
    }

    ctx.putImageData(imageData, 0, 0);

    // Create image overlay
    const bounds = L.latLngBounds(
      [min_lat, min_lon],
      [max_lat, max_lon]
    );

    const overlay = L.imageOverlay(canvas.toDataURL(), bounds, {
      opacity: 0.6,
      interactive: false,
    });

    overlay.addTo(map);

    return () => {
      overlay.remove();
    };
  }, [data, map]);

  return null;
};

export default RiskHeatmap;