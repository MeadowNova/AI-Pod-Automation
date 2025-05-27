import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ChartBarIcon,
  Cog6ToothIcon,
  HomeIcon,
  LightBulbIcon,
  PhotoIcon,
  PuzzlePieceIcon,
  SparklesIcon,
  ArrowLeftOnRectangleIcon,
  AdjustmentsHorizontalIcon // Using AdjustmentsHorizontalIcon for SEO, or another suitable one like TagIcon if available
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Trends', href: '/dashboard/trends', icon: LightBulbIcon },
  { name: 'AI Studio', href: '/dashboard/ai-studio', icon: SparklesIcon },
  { name: 'Mockups', href: '/dashboard/mockups', icon: PhotoIcon },
  { name: 'Listings', href: '/dashboard/listings', icon: PuzzlePieceIcon },
  { name: 'SEO Optimizer', href: '/dashboard/seo-optimizer', icon: AdjustmentsHorizontalIcon }, // Added SEO Optimizer link
  { name: 'Analytics', href: '/dashboard/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/dashboard/settings', icon: Cog6ToothIcon },
];

const Sidebar: React.FC = () => {
  // Mock user for development mode
  const displayUser = {
    name: 'Development User',
    email: 'dev@example.com'
  };
  const handleLogout = () => console.log('🔧 Dev mode: Logout disabled');

  return (
    <aside className="bg-dark-bg text-dark-text-secondary w-64 p-4 flex flex-col shadow-lg">
      <div className="mb-8">
        {/* Logo Placeholder */}
        <div className="text-dark-text text-2xl font-bold text-center py-4">
          POD Co-Pilot
        </div>
      </div>
      <nav className="flex-1 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `group flex items-center px-3 py-2 text-sm font-medium rounded-md ${isActive
                ? 'bg-dark-card text-dark-text'
                : 'hover:bg-dark-card hover:text-dark-text'
              }`
            }
          >
            <item.icon className="mr-3 h-6 w-6 flex-shrink-0" aria-hidden="true" />
            {item.name}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto">
        {/* User Info */}
        <div className="mb-3 px-3 py-2 text-sm text-dark-text-secondary">
          Welcome, {displayUser.name}
          <div className="text-xs text-yellow-400 mt-1">🔧 Dev Mode</div>
        </div>
        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="group flex w-full items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-dark-card hover:text-dark-text"
        >
          <ArrowLeftOnRectangleIcon className="mr-3 h-6 w-6 flex-shrink-0" aria-hidden="true" />
          Logout (Disabled)
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;

