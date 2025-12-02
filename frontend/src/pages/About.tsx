import React from 'react';
import { APP_INFO } from '@/utils/constants';

const About: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {APP_INFO.NAME}
          </h1>

          <div className="space-y-6 text-gray-600">
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">About</h2>
              <p>{APP_INFO.DESCRIPTION}</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Features</h2>
              <ul className="list-disc list-inside space-y-1">
                <li>Real-time river gauge monitoring</li>
                <li>Flood risk predictions using AI/ML</li>
                <li>Interactive map visualization</li>
                <li>WebSocket-based live updates</li>
                <li>Historical data analysis</li>
                <li>Risk zone mapping</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Data Sources</h2>
              <ul className="list-disc list-inside space-y-1">
                <li>USGS Water Services API (River Gauges)</li>
                <li>NOAA Weather API (Precipitation Forecasts)</li>
                <li>PostGIS Spatial Database</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Technology Stack</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-medium text-gray-900">Frontend</h3>
                  <ul className="text-sm space-y-1 mt-1">
                    <li>React + TypeScript</li>
                    <li>Tailwind CSS</li>
                    <li>Leaflet Maps</li>
                    <li>Socket.IO Client</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Backend</h3>
                  <ul className="text-sm space-y-1 mt-1">
                    <li>FastAPI (Python)</li>
                    <li>PostgreSQL + PostGIS</li>
                    <li>SQLAlchemy</li>
                    <li>Celery (Background Tasks)</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="pt-4 border-t border-gray-200">
              <p className="text-sm">
                <strong>Version:</strong> {APP_INFO.VERSION}<br />
                <strong>Author:</strong> {APP_INFO.AUTHOR}
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;