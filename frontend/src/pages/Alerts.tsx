import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '@/components/Layout/Header';
import { formatRelativeTime } from '@/utils/formatters';

interface Alert {
  id: number;
  type: 'flood_warning' | 'flood_watch' | 'flash_flood' | 'high_water';
  severity: 'severe' | 'high' | 'moderate' | 'low';
  title: string;
  message: string;
  affected_areas: string[];
  issued_at: string;
  expires_at: string;
  is_active: boolean;
}

// Mock alerts - Replace with actual API
const mockAlerts: Alert[] = [
  {
    id: 1,
    type: 'flood_warning',
    severity: 'severe',
    title: 'Flood Warning for Potomac River',
    message: 'The National Weather Service has issued a Flood Warning for the Potomac River at Washington DC. River levels are expected to reach 14.5 feet by midnight.',
    affected_areas: ['Washington DC', 'Arlington', 'Alexandria'],
    issued_at: new Date(Date.now() - 3600000).toISOString(),
    expires_at: new Date(Date.now() + 7200000).toISOString(),
    is_active: true,
  },
  {
    id: 2,
    type: 'flash_flood',
    severity: 'high',
    title: 'Flash Flood Watch',
    message: 'Heavy rainfall expected in the next 6 hours. Flash flooding possible in urban areas and near small streams.',
    affected_areas: ['Rock Creek', 'Anacostia River Basin'],
    issued_at: new Date(Date.now() - 1800000).toISOString(),
    expires_at: new Date(Date.now() + 21600000).toISOString(),
    is_active: true,
  },
];

const Alerts: React.FC = () => {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<'all' | 'active' | 'expired'>('all');

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = () => {
    setAlerts(mockAlerts);
  };

  const filteredAlerts = alerts.filter((alert) => {
    if (filter === 'all') return true;
    if (filter === 'active') return alert.is_active;
    return !alert.is_active;
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'severe':
        return 'bg-red-100 border-red-500 text-red-900';
      case 'high':
        return 'bg-orange-100 border-orange-500 text-orange-900';
      case 'moderate':
        return 'bg-yellow-100 border-yellow-500 text-yellow-900';
      default:
        return 'bg-blue-100 border-blue-500 text-blue-900';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'flood_warning':
        return (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        );
      case 'flash_flood':
        return (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        );
      default:
        return (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        );
    }
  };

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

        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Flood Alerts & Warnings</h1>
          <p className="text-gray-600">Active flood warnings and watches for your area</p>
        </div>

        {/* Filter Tabs */}
        <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
          <div className="flex gap-2">
            {['all', 'active', 'expired'].map((tab) => (
              <button
                key={tab}
                onClick={() => setFilter(tab as any)}
                className={`px-4 py-2 rounded-lg font-medium transition capitalize ${
                  filter === tab
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Alerts List */}
        <div className="space-y-4">
          {filteredAlerts.length === 0 ? (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <svg
                className="w-16 h-16 mx-auto text-green-500 mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-xl font-semibold text-gray-900 mb-2">No Active Alerts</p>
              <p className="text-gray-600">There are currently no flood alerts for your area</p>
            </div>
          ) : (
            filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`rounded-lg border-l-4 p-6 shadow-lg ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start">
                  <div className="shrink-0">
                    <svg
                      className="w-8 h-8"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      {getAlertIcon(alert.type)}
                    </svg>
                  </div>

                  <div className="ml-4 flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-xl font-bold mb-2">{alert.title}</h3>
                        <p className="text-sm uppercase font-semibold mb-3">
                          {alert.type.replace('_', ' ')} • {alert.severity}
                        </p>
                      </div>
                      {alert.is_active && (
                        <span className="px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full uppercase">
                          Active
                        </span>
                      )}
                    </div>

                    <p className="mb-4">{alert.message}</p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-sm font-semibold mb-1">Affected Areas</p>
                        <p className="text-sm">{alert.affected_areas.join(', ')}</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold mb-1">Issued</p>
                        <p className="text-sm">{formatRelativeTime(alert.issued_at)}</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold mb-1">Expires</p>
                        <p className="text-sm">{formatRelativeTime(alert.expires_at)}</p>
                      </div>
                    </div>

                    <button className="px-4 py-2 bg-white bg-opacity-50 hover:bg-opacity-70 rounded-lg font-medium transition">
                      View Full Details →
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Alerts;