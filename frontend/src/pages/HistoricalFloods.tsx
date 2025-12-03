import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "@/components/Layout/Header";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import { formatDate, formatGaugeHeight } from "@/utils/formatters";
import { apiService } from "@/services/api";

interface HistoricalFlood {
  id: number;
  event_name: string;
  event_date: string;
  location_name: string | null;
  severity: string;
  peak_gauge_height_ft: number | null;
  peak_flow_cfs: number | null;
  estimated_damage_usd: number | null;
  casualties: number;
  evacuations: number;
  description: string | null;
  verified: boolean;
  created_at: string;
}

interface FloodStatistics {
  total_events: number;
  by_severity: Record<string, number>;
  total_damage_usd: number;
  total_casualties: number;
  total_evacuations: number;
  average_damage_per_event: number;
}

const HistoricalFloods: React.FC = () => {
  const navigate = useNavigate();
  const [floods, setFloods] = useState<HistoricalFlood[]>([]);
  const [statistics, setStatistics] = useState<FloodStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHistoricalData();
  }, [filter]);

  const loadHistoricalData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Load floods with optional severity filter
      const params =
        filter !== "all" ? { severity: filter, limit: 100 } : { limit: 100 };
      const floodsData = await apiService.getHistoricalFloods(params);
      setFloods(floodsData);

      // Load statistics
      const stats = await apiService.getFloodStatistics();
      setStatistics(stats);
    } catch (err) {
      console.error("Error loading historical data:", err);
      setError("Failed to load historical flood data. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const filteredFloods = floods.filter((flood) => {
    if (filter === "all") return true;
    return flood.severity === filter;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Header connected={false} />

      <div className="container mx-auto px-4 py-8">
        <button
          onClick={() => navigate("/")}
          className="mb-4 flex items-center gap-2 text-blue-600 hover:text-blue-700"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Dashboard
        </button>

        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Historical Flood Events
          </h1>
          <p className="text-gray-600">
            View past flood events and their impact
          </p>
        </div>

        {/* Statistics Summary */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-lg p-4">
              <p className="text-sm text-gray-600">Total Events</p>
              <p className="text-2xl font-bold text-gray-900">
                {statistics.total_events}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-lg p-4">
              <p className="text-sm text-gray-600">Total Damage</p>
              <p className="text-2xl font-bold text-gray-900">
                ${(statistics.total_damage_usd / 1000000).toFixed(1)}M
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-lg p-4">
              <p className="text-sm text-gray-600">Casualties</p>
              <p className="text-2xl font-bold text-gray-900">
                {statistics.total_casualties}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-lg p-4">
              <p className="text-sm text-gray-600">Evacuations</p>
              <p className="text-2xl font-bold text-gray-900">
                {statistics.total_evacuations}
              </p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
          <div className="flex gap-2">
            {["all", "minor", "moderate", "major", "catastrophic"].map(
              (severity) => (
                <button
                  key={severity}
                  onClick={() => setFilter(severity)}
                  className={`px-4 py-2 rounded-lg font-medium transition capitalize ${
                    filter === severity
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {severity}
                </button>
              )
            )}
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" message="Loading historical data..." />
          </div>
        ) : (
          <div className="space-y-4">
            {filteredFloods.length === 0 ? (
              <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                <p className="text-gray-600">
                  No historical flood events found
                </p>
              </div>
            ) : (
              filteredFloods.map((flood) => (
                <div
                  key={flood.id}
                  className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-xl font-bold text-gray-900">
                          {flood.event_name}
                        </h3>
                        {flood.verified && (
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                            Verified
                          </span>
                        )}
                      </div>
                      {flood.location_name && (
                        <p className="text-gray-600 mb-2">
                          {flood.location_name}
                        </p>
                      )}
                      {flood.description && (
                        <p className="text-gray-600 mb-4">
                          {flood.description}
                        </p>
                      )}

                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-gray-600">Date</p>
                          <p className="font-medium">
                            {formatDate(flood.event_date)}
                          </p>
                        </div>
                        {flood.peak_gauge_height_ft && (
                          <div>
                            <p className="text-sm text-gray-600">Peak Height</p>
                            <p className="font-medium">
                              {formatGaugeHeight(flood.peak_gauge_height_ft)}
                            </p>
                          </div>
                        )}
                        <div>
                          <p className="text-sm text-gray-600">Severity</p>
                          <span
                            className={`inline-block px-3 py-1 rounded-full text-sm font-semibold capitalize ${
                              flood.severity === "catastrophic"
                                ? "bg-red-100 text-red-800"
                                : flood.severity === "major"
                                ? "bg-orange-100 text-orange-800"
                                : flood.severity === "moderate"
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-blue-100 text-blue-800"
                            }`}
                          >
                            {flood.severity}
                          </span>
                        </div>
                        {flood.estimated_damage_usd && (
                          <div>
                            <p className="text-sm text-gray-600">
                              Estimated Damage
                            </p>
                            <p className="font-medium">
                              $
                              {(flood.estimated_damage_usd / 1000000).toFixed(
                                1
                              )}
                              M
                            </p>
                          </div>
                        )}
                      </div>
                    </div>

                    <button
                      onClick={() => navigate(`/historical/${flood.id}`)}
                      className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                      View Details
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoricalFloods;
