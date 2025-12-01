import React, { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

interface PrecipitationData {
  timestamp: string;
  intensity: number; // inches per hour
  coordinates: [number, number][];
}

interface PrecipitationOverlayProps {
  data: PrecipitationData[];
  opacity?: number;
}

const PrecipitationOverlay: React.FC<PrecipitationOverlayProps> = ({ 
  data, 
  opacity = 0.6 
}) => {
  const map = useMap();

  useEffect(() => {
    if (!data || data.length === 0) return;

    const layers: L.Layer[] = [];

    // Create precipitation overlay for each data point
    data.forEach((precip) => {
      // Get color based on intensity
      const color = getIntensityColor(precip.intensity);
      
      // Create circle markers for precipitation
      precip.coordinates.forEach((coord) => {
        const circle = L.circle([coord[1], coord[0]], {
          color: color,
          fillColor: color,
          fillOpacity: opacity,
          radius: 5000, // 5km radius
          weight: 1,
        });

        circle.addTo(map);
        layers.push(circle);

        // Add popup with precipitation info
        circle.bindPopup(`
          <div class="p-2">
            <strong>Precipitation</strong><br/>
            <span class="text-sm">
              ${precip.intensity.toFixed(2)} in/hr<br/>
              ${new Date(precip.timestamp).toLocaleString()}
            </span>
          </div>
        `);
      });
    });

    // Cleanup on unmount
    return () => {
      layers.forEach((layer) => layer.remove());
    };
  }, [data, map, opacity]);

  return null;
};

// Helper function to get color based on precipitation intensity
const getIntensityColor = (intensity: number): string => {
  // intensity in inches per hour
  if (intensity >= 2.0) return '#8B0000'; // Dark red - extreme
  if (intensity >= 1.0) return '#FF0000'; // Red - heavy
  if (intensity >= 0.5) return '#FF8C00'; // Orange - moderate
  if (intensity >= 0.1) return '#FFD700'; // Yellow - light
  return '#87CEEB'; // Light blue - trace
};

export default PrecipitationOverlay;
