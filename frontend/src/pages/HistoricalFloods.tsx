import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '@/components/Layout/Header';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import { formatDate, formatGaugeHeight } from '@/utils/formatters';

interface HistoricalFlood {
  id: number;
  gauge_name: string;
  date: string;
  peak_height_ft: number;
  stage: string;
  description: string;
}

// Mock data - Replace with actual API call
const mockHistoricalFloods: HistoricalFlood[] = [
  {
    id: 1,
    gauge_name: 'Potomac River at Washington DC',
    date: '2024-09-28T14:30:00Z',
    peak_height_ft: 15.2,
    stage: 'flood',
    description: 'Heavy rainfall from tropical storm caused moderate flooding',
  },
  {
    id: 2,
    gauge_name: 'Rock Creek at Sherrill Drive',
    date: '2024-08-15T09:15:00Z',
    peak_height_ft: 8.5,
    stage: 'action',
    description: 'Flash flood warning issued, roads temporarily closed',
  },
  {
    id: 3,
    gauge_name: 'Anacostia River at Bladensburg',
    date: '2024-07-04T16:45:00Z',
    peak_height_ft: 12.8,
    stage: 'flood',
    description: 'Independence Day storm caused flooding in low-lying areas',
  },
];

const HistoricalFloods: React.FC = () => {
  const navigate = useNavigate();
  const [floods, setFloods] = useState<HistoricalFlood[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    loadHistoricalData();
  }, []);

  const loadHistoricalData = async () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setFloods(mockHistoricalFloods);
      setLoading(false);
    }, 1000);
  };

  const filteredFloods = floods.filter((flood) => {
    if (filter === 'all') return true;
    return flood.stage === filter;
  });

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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Historical Flood Events</h1>
          <p className="text-gray-600">View past flood events and their impact</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
          <div className="flex gap-2">
            {['all', 'major', 'flood', 'action'].map((stage) => (
              <button
                key={stage}
                onClick={() => setFilter(stage)}
                className={`px-4 py-2 rounded-lg font-medium transition capitalize ${
                  filter === stage
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {stage}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" message="Loading historical data..." />
          </div>
        ) : (
          <div className="space-y-4">
            {filteredFloods.length === 0 ? (
              <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                <p className="text-gray-600">No historical flood events found</p>
              </div>
            ) : (
              filteredFloods.map((flood) => (
                <div key={flood.id} className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{flood.gauge_name}</h3>
                      <p className="text-gray-600 mb-4">{flood.description}</p>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <p className="text-sm text-gray-600">Date</p>
                          <p className="font-medium">{formatDate(flood.date)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Peak Height</p>
                          <p className="font-medium">{formatGaugeHeight(flood.peak_height_ft)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Stage</p>
                          <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold capitalize ${
                            flood.stage === 'major' ? 'bg-red-100 text-red-800' :
                            flood.stage === 'flood' ? 'bg-orange-100 text-orange-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {flood.stage}
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
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