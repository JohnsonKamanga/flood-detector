import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ErrorBoundary from '@/components/shared/ErrorBoundary';

// Pages
import Dashboard from '@/pages/Dashboard';
import GaugeDetails from '@/pages/GaugeDetails';
import RiskAssessment from '@/pages/RiskAssessment';
import HistoricalFloods from '@/pages/HistoricalFloods';
import Alerts from '@/pages/Alerts';
import About from '@/pages/About';
import NotFound from '@/pages/NotFound';

import { validateEnvironmentVariables } from '@/utils/dataValidation';

// Validate environment variables on app load
try {
  validateEnvironmentVariables();
} catch (error) {
  console.error('Environment validation failed:', error);
  if (import.meta.env.DEV) {
    console.error('Please check your .env file and ensure all required variables are set.');
  }
}

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          {/* Main Dashboard */}
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />

          {/* Gauge Details */}
          <Route path="/gauge/:gaugeId" element={<GaugeDetails />} />

          {/* Risk Assessment */}
          <Route path="/risk-assessment" element={<RiskAssessment />} />

          {/* Historical Data */}
          <Route path="/historical" element={<HistoricalFloods />} />

          {/* Alerts */}
          <Route path="/alerts" element={<Alerts />} />

          {/* About */}
          <Route path="/about" element={<About />} />

          {/* 404 */}
          <Route path="/404" element={<NotFound />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
};

export default App;