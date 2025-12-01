import React from 'react';

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
    <header className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
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

          {/* Actions */}
          <div className="flex items-center gap-4">
            {/* Connection Status */}
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

            {/* Heatmap Toggle */}
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

            {/* Settings Button */}
            <button
              className="p-2 hover:bg-blue-700 rounded-lg transition"
              aria-label="Settings"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
