import { Outlet, useLocation } from 'react-router-dom';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import { ThemeProvider } from '../contexts/ThemeContext';

const AppLayout = () => {
  // Try to use location, but provide a fallback for when not in a Router context
  let pageTitle = '';
  try {
    const location = useLocation();

    // Get the current page title based on the route
    const path = location.pathname;

    if (path === '/') pageTitle = 'Dashboard';
    else if (path === '/trends') pageTitle = 'Trend Spotting';
    else if (path === '/ai-studio') pageTitle = 'AI Design Studio';
    else if (path === '/mockups') pageTitle = 'Mockup Generator';
    else if (path === '/listings') pageTitle = 'Listings Manager';
    else if (path === '/analytics') pageTitle = 'Analytics';
    else if (path === '/settings') pageTitle = 'Settings';
  } catch (error) {
    // If useLocation fails, we're probably not in a Router context
    console.warn('AppLayout: Not in a Router context');
  }

  return (
    <ThemeProvider>
      <div className="flex h-screen bg-light-bg dark:bg-dark-bg">
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden">
          <Header title={pageTitle} />
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-light-bg dark:bg-dark-bg p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
};

export default AppLayout;
