import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";
import AppLayout from "./layouts/AppLayout";
import DashboardPage from "./pages/DashboardPage";
import TrendsPage from "./pages/TrendsPage";
import AIStudioPage from "./pages/AIStudioPage";
import MockupsPage from "./pages/MockupsPage";
import ListingsPage from "./pages/ListingsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import SettingsPage from "./pages/SettingsPage";
import LoginPage from "./pages/LoginPage"; // Assuming a login page is needed
import LandingPage from "./pages/LandingPage"; // Assuming a landing page outside the app layout
import PricingPage from "./pages/PricingPage"; // Assuming a pricing page outside the app layout

import './index.css'

function App() {
  return (
    <Router>
      <Routes>
        {/* Routes outside the main app layout */}
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Routes within the main app layout */}
        <Route path="/" element={<AppLayout />}>
          <Route index element={<DashboardPage />} /> {/* Default route */}
          <Route path="trends" element={<TrendsPage />} />
          <Route path="ai-studio" element={<AIStudioPage />} />
          <Route path="mockups" element={<MockupsPage />} />
          <Route path="listings" element={<ListingsPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* TODO: Add a 404 Not Found route */}
      </Routes>
    </Router>
  );
}

export default App;
