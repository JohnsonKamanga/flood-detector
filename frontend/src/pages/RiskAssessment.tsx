import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import Header from '@/components/Layout/Header';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import ErrorMessage from '@/components/shared/ErrorMessage';
import { formatRiskScore, formatConfidence } from '@/utils/formatters';
import { MapContainer, TileLayer, Marker, Circle, Popup } from 'react-leaflet';
import { MAP_CONFIG } from '@/utils/constants';

const RiskAssessment: React.FC = () => {
  const navigate = useNavigate();
  const [latitude, setLatitude] = useState<string>('');
  const [longitude, setLongitude] = useState<string>('');
  const [radius, setRadius] = useState<number>(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const lat = parseFloat(latitude);
    const lon = parseFloat(longitude);

    if (isNaN(lat) || isNaN(lon)) {
      setError('Please enter valid coordinates');
      return;
    }

    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      setError('Coordinates out of range');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const data = await apiService.calculateRisk({
        latitude: lat,
        longitude: lon,
        radius_km: radius,
      });

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to calculate risk');
    } finally {
      setLoading(false);
    }
  };

  const useCurrentLocation = () => {
    if ('geolocation' in navigator) {
      setLoading(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude.toFixed(6));
          setLongitude(position.coords.longitude.toFixed(6));
          setLoading(false);
        },
        (error) => {
            console.error("Failed to get current location: ", error);
          setError('Failed to get current location');
          setLoading(false);
        }
      );
    } else {
      setError('Geolocation is not supported by your browser');
    }
  };

  const riskInfo = result ? formatRiskScore(result.risk_assessment.composite_score) : null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header connected={false} />

      <div className="container mx-auto px-4 py-8">
        <button
          onClick={() => navigate('/')}
          className="mb-4 flex items-center gap-2 text-blue-600 hover:text-blue-700"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Dashboard
        </button>

        <h1 className="text-3xl font-bold text-gray-900 mb-6">Flood Risk Assessment</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Form */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Enter Location</h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Latitude
                </label>
                <input
                  type="number"
                  step="any"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  placeholder="38.9072"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Longitude
                </label>
                <input
                  type="number"
                  step="any"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  placeholder="-77.0369"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Search Radius (km)
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={radius}
                  onChange={(e) => setRadius(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Calculating...' : 'Calculate Risk'}
                </button>
                <button
                  type="button"
                  onClick={useCurrentLocation}
                  disabled={loading}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition disabled:opacity-50"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </button>
              </div>
            </form>

            {error && (
              <div className="mt-4">
                <ErrorMessage message={error} type="error" onDismiss={() => setError(null)} />
              </div>
            )}

            {loading && (
              <div className="mt-4 flex justify-center">
                <LoadingSpinner message="Calculating flood risk..." />
              </div>
            )}
          </div>

          {/* Results */}
          {result && riskInfo && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Risk Assessment Results</h2>

              {/* Overall Risk */}
              <div className={`p-6 rounded-lg mb-6 ${riskInfo.bgColor}`}>
                <p className="text-sm text-gray-600 mb-2">Overall Risk Level</p>
                <p className={`text-4xl font-bold ${riskInfo.textColor}`}>{riskInfo.label}</p>
                <p className="text-lg mt-2">
                  Score: {result.risk_assessment.composite_score.toFixed(1)}/100
                </p>
                <p className="text-sm mt-1">
                  Confidence: {formatConfidence(result.risk_assessment.confidence)}
                </p>
              </div>

              {/* Risk Components */}
              <div className="space-y-3 mb-6">
                <h3 className="font-semibold text-gray-900">Risk Factors</h3>

                {Object.entries(result.risk_assessment.components).map(([key, value]: [string, any]) => (
                  <div key={key} className="bg-gray-50 rounded-lg p-3">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {key.replace('_', ' ')}
                      </span>
                      <span className="text-sm font-bold">{value.toFixed(1)}/100</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${value}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Nearby Gauges */}
              {result.nearby_gauges && result.nearby_gauges.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Nearby Gauges</h3>
                  <div className="space-y-2">
                    {result.nearby_gauges.map((gauge: any, index: number) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-3">
                        <p className="font-medium text-gray-900">{gauge.name}</p>
                        <p className="text-sm text-gray-600">
                          Stage: <span className="capitalize">{gauge.current_stage || 'Unknown'}</span>
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Map */}
          {result && (
            <div className="lg:col-span-2 bg-white rounded-lg shadow-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Location Map</h3>
              <div className="h-96 rounded-lg overflow-hidden">
                <MapContainer
                  center={[result.location.latitude, result.location.longitude]}
                  zoom={10}
                  className="h-full w-full"
                >
                  <TileLayer
                    url={MAP_CONFIG.TILE_LAYER_URL}
                    attribution={MAP_CONFIG.TILE_LAYER_ATTRIBUTION}
                  />
                  <Marker position={[result.location.latitude, result.location.longitude]}>
                    <Popup>
                      <div className="p-2">
                        <p className="font-medium">Assessment Location</p>
                        <p className="text-sm">Risk: {riskInfo?.label}</p>
                      </div>
                    </Popup>
                  </Marker>
                  <Circle
                    center={[result.location.latitude, result.location.longitude]}
                    radius={radius * 1000}
                    pathOptions={{ color: riskInfo?.color, fillColor: riskInfo?.color, fillOpacity: 0.2 }}
                  />
                </MapContainer>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RiskAssessment;