import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ErrorBoundary from './components/ErrorBoundary';
import Dashboard from './pages/Dashboard';
import GeneratePlan from './pages/GeneratePlan';
import Corridors from './pages/Corridors';
import Assets from './pages/Assets';
import MaintenanceTasks from './pages/MaintenanceTasks';
import Settings from './pages/Settings';
import BlockAvailability from './pages/BlockAvailability';
import Trains from './pages/Trains';
import Schedules from './pages/Schedules';
import Resources from './pages/Resources';
import Reports from './pages/Reports';
import Alerts from './pages/Alerts';
import Admin from './pages/Admin';
import AIPriority from './pages/AIPriority';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ErrorBoundary><Dashboard /></ErrorBoundary>} />
          <Route path="corridors" element={<ErrorBoundary><Corridors /></ErrorBoundary>} />
          <Route path="plans" element={<ErrorBoundary><GeneratePlan /></ErrorBoundary>} />
          <Route path="plan/generate" element={<ErrorBoundary><GeneratePlan /></ErrorBoundary>} />
          <Route path="trains" element={<ErrorBoundary><Trains /></ErrorBoundary>} />
          <Route path="schedules" element={<ErrorBoundary><Schedules /></ErrorBoundary>} />
          <Route path="resources" element={<ErrorBoundary><Resources /></ErrorBoundary>} />
          <Route path="assets" element={<ErrorBoundary><Assets /></ErrorBoundary>} />
          <Route path="maintenance" element={<ErrorBoundary><MaintenanceTasks /></ErrorBoundary>} />
          <Route path="ai-priority" element={<ErrorBoundary><AIPriority /></ErrorBoundary>} />
          <Route path="blocks" element={<ErrorBoundary><BlockAvailability /></ErrorBoundary>} />
          <Route path="reports" element={<ErrorBoundary><Reports /></ErrorBoundary>} />
          <Route path="alerts" element={<ErrorBoundary><Alerts /></ErrorBoundary>} />
          <Route path="settings" element={<ErrorBoundary><Settings /></ErrorBoundary>} />
          <Route path="admin" element={<ErrorBoundary><Admin /></ErrorBoundary>} />
          <Route path="*" element={<div className="p-6"><h1 className="text-2xl font-bold text-red-500">404 - Page Not Found</h1></div>} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
