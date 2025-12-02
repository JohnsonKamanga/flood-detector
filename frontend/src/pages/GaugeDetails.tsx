import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import type { GaugeData, GaugeMeasurement } from '@/types/flood.types';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import ErrorMessage from '@/components/shared/ErrorMessage';
import Header from '@/components/Layout/Header';
import {
  formatFlowRate,
  formatGaugeHeight,
  formatRelativeTime,
  formatStage,
  formatDate,
} from '@/utils/formatters';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const GaugeDetails: React.FC = () => {
  const { gaugeId } = useParams<{ gaugeId: string }>();
  const navigate = useNavigate();
  const [gauge, setGauge] = useState<GaugeData | null>(null);
  const [measurements, setMeasurements] = useState<GaugeMeasurement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<number>(24); // hours

  useEffect(() => {
    loadGaugeData();
  }, [gaugeId, timeRange]);

  const loadGaugeData = async () => {
    if (!gaugeId) return;

    try {
      setLoading(true);
      setError(null);

      const [gaugeData, measurementsData] = await Promise.all([
        apiService.getGauge(parseInt(gaugeId)),
        apiService.getGaugeMeasurements(parseInt(gaugeId), timeRange),
      ]);

      setGauge(gaugeData);
      setMeasurements(measurementsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load gauge data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header connected={false} />
        <div className="flex items-center justify-center h-screen">
          <LoadingSpinner size="lg" message="Loading gauge details..." />
        </div>
      </div>
    );
  }

  if (error || !gauge) {
    return (
      <div className="min-h-screen">
        <Header connected={false} />
        <div className="flex items-center justify-center h-screen p-4">
          <ErrorMessage
            message={error || 'Gauge not found'}
            title="Error"
            onRetry={loadGaugeData}
          />
        </div>
      </div>
    );
  }

  const stageInfo = formatStage(gauge.current_stage);

  // Prepare chart data
  const chartData = measurements
    .map((m) => ({
      timestamp: new Date(m.timestamp).getTime(),
      time: formatDate(m.timestamp, 'MM/dd HH:mm'),
      height: m.gauge_height_ft,
      flow: m.flow_cfs,
    }))
    .reverse();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header connected={false} />

      <div className="container mx-auto px-4 py-8">
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          className="mb-4 flex items-center gap-2 text-blue-600 hover:text-blue-700"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Dashboard
        </button>

        {/* Gauge Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{gauge.name}</h1>
              <p className="text-gray-600">Site ID: {gauge.usgs_site_id}</p>
            </div>
            <div className={`px-4 py-2 rounded-lg ${stageInfo.bgColor}`}>
              <span className="text-white font-bold text-lg">{stageInfo.label}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Current Height</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatGaugeHeight(gauge.current_gauge_height_ft)}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Current Flow</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatFlowRate(gauge.current_flow_cfs)}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Last Updated</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatRelativeTime(gauge.last_updated)}
              </p>
            </div>
          </div>

          {/* Thresholds */}
          <div className="mt-6">
            <h3 className="font-semibold text-gray-900 mb-3">Flood Stage Thresholds</h3>
            <div className="space-y-2">
              {gauge.action_stage_ft && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Action Stage</span>
                  <span className="font-medium">{formatGaugeHeight(gauge.action_stage_ft)}</span>
                </div>
              )}
              {gauge.flood_stage_ft && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Flood Stage</span>
                  <span className="font-medium">{formatGaugeHeight(gauge.flood_stage_ft)}</span>
                </div>
              )}
              {gauge.major_flood_stage_ft && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Major Flood Stage</span>
                  <span className="font-medium">{formatGaugeHeight(gauge.major_flood_stage_ft)}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Time Range Selector */}
        <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">Historical Data</h2>
            <div className="flex gap-2">
              {[6, 12, 24, 48, 168].map((hours) => (
                <button
                  key={hours}
                  onClick={() => setTimeRange(hours)}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    timeRange === hours
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {hours < 24 ? `${hours}h` : `${hours / 24}d`}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gauge Height Chart */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Gauge Height</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis label={{ value: 'Height (ft)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="height"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  name="Gauge Height"
                  dot={false}
                />
                {gauge.action_stage_ft && (
                  <Line
                    type="monotone"
                    dataKey={() => gauge.action_stage_ft}
                    stroke="#CA8A04"
                    strokeDasharray="5 5"
                    name="Action Stage"
                    dot={false}
                  />
                )}
                {gauge.flood_stage_ft && (
                  <Line
                    type="monotone"
                    dataKey={() => gauge.flood_stage_ft}
                    stroke="#EA580C"
                    strokeDasharray="5 5"
                    name="Flood Stage"
                    dot={false}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Flow Rate Chart */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Flow Rate</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis label={{ value: 'Flow (cfs)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="flow"
                  stroke="#10B981"
                  strokeWidth={2}
                  name="Flow Rate"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Location Info */}
        <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Location Information</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Latitude</p>
              <p className="font-medium">{gauge.latitude.toFixed(4)}°</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Longitude</p>
              <p className="font-medium">{gauge.longitude.toFixed(4)}°</p>
            </div>
            {gauge.elevation_ft && (
              <div>
                <p className="text-sm text-gray-600">Elevation</p>
                <p className="font-medium">{gauge.elevation_ft.toFixed(0)} ft</p>
              </div>
            )}
            {gauge.drainage_area_sqmi && (
              <div>
                <p className="text-sm text-gray-600">Drainage Area</p>
                <p className="font-medium">{gauge.drainage_area_sqmi.toFixed(0)} sq mi</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GaugeDetails;