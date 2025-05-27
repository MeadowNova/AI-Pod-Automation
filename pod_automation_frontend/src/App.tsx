import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import AppLayout from "./layouts/AppLayout";
import DashboardPage from "./pages/DashboardPage";
import TrendsPage from "./pages/TrendsPage";
import AIStudioPage from "./pages/AIStudioPage";
import MockupsPage from "./pages/MockupsPage";
import ListingsPage from "./pages/ListingsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import SettingsPage from "./pages/SettingsPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import LandingPage from "./pages/LandingPage";
import PricingPage from "./pages/PricingPage";
import SEOOptimizerPage from "./pages/SEOOptimizerPage"; // Import the new SEO Optimizer page

import './index.css'

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes outside the main app layout */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/login" element={<Navigate to="/dashboard" replace />} />
        <Route path="/signup" element={<Navigate to="/dashboard" replace />} />

        {/* All routes are now unprotected for development */}
        <Route path="/dashboard" element={<AppLayout />}>
          <Route index element={<DashboardPage />} /> {/* Default route for /dashboard */}
          <Route path="trends" element={<TrendsPage />} />
          <Route path="ai-studio" element={<AIStudioPage />} />
          <Route path="mockups" element={<MockupsPage />} />
          <Route path="listings" element={<ListingsPage />} />
          <Route path="seo-optimizer" element={<SEOOptimizerPage />} /> {/* Add route for SEO Optimizer */}
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* Legacy /app routes - redirect to /dashboard */}
        <Route path="/app/*" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="trends" element={<TrendsPage />} />
          <Route path="ai-studio" element={<AIStudioPage />} />
          <Route path="mockups" element={<MockupsPage />} />
          <Route path="listings" element={<ListingsPage />} />
          <Route path="seo-optimizer" element={<SEOOptimizerPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* TODO: Add a 404 Not Found route */}
      </Routes>
    </Router>
  );
}

export default App;

