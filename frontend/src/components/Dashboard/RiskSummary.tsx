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

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h2 className="text-lg font-semibold mb-4">System Overview</h2>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-blue-50 rounded">
          <div className="text-3xl font-bold text-blue-600">{totalGauges}</div>
          <div className="text-sm text-gray-600">Active Gauges</div>
        </div>

        <div className="text-center p-3 bg-red-50 rounded">
          <div className="text-3xl font-bold text-red-600">{highRiskCount}</div>
          <div className="text-sm text-gray-600">High Risk</div>
        </div>
      </div>

      {latestPrediction && (
        <div className={`p-3 rounded border ${getRiskColor(latestPrediction.risk_level)}`}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">Current Risk Level</span>
            <span className="text-xs">
              Score: {latestPrediction.risk_score.toFixed(1)}
            </span>
          </div>
          <div className="text-2xl font-bold capitalize">{latestPrediction.risk_level}</div>
          {latestPrediction.confidence && (
            <div className="text-xs mt-1">
              Confidence: {(latestPrediction.confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RiskSummary;     
