import React from 'react';
import NavigationMenu from './NavigationMenu';

interface HeaderProps {
  connected: boolean;
  onToggleHeatmap?: () => void;
  showHeatmap?: boolean;
}

const Header: React.FC<HeaderProps> = ({ 
  connected, 
  onToggleHeatmap, 
  showHeatmap = false 
}) => {
  return (
    <div>
      <header className="bg-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold">Urban Flood Prediction System</h1>
                <p className="text-sm text-blue-100">Real-time monitoring and predictions</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1 bg-blue-700 rounded-full">
                <div
                  className={`w-2 h-2 rounded-full ${
                    connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
                  }`}
                />
                <span className="text-sm font-medium">
                  {connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              {onToggleHeatmap && (
                <button
                  onClick={onToggleHeatmap}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    showHeatmap
                      ? 'bg-white text-blue-600 hover:bg-blue-50'
                      : 'bg-blue-700 text-white hover:bg-blue-800'
                  }`}
                >
                  {showHeatmap ? 'Hide Heatmap' : 'Show Heatmap'}
                </button>
              )}
            </div>
          </div>
        </div>
      </header>
      <NavigationMenu />
    </div>
  );
};

export default Header;