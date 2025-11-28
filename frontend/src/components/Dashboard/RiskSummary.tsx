import React from 'react';
import type { FloodPrediction } from '@/types/flood.types';

interface RiskSummaryProps {
  totalGauges: number;
  highRiskCount: number;
  predictions: FloodPrediction[];
}

const RiskSummary: React.FC<RiskSummaryProps> = ({ totalGauges, highRiskCount, predictions }) => {
  const latestPrediction = predictions.length > 0 ? predictions[0] : null;

  const getRiskColor = (level: string): string => {
    switch (level) {
      case 'severe':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'moderate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
      default:
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };