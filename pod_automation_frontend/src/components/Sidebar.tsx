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
  { name: 'Dashboard', href: '/app', icon: HomeIcon },
  { name: 'Trends', href: '/app/trends', icon: LightBulbIcon },
  { name: 'AI Studio', href: '/app/ai-studio', icon: SparklesIcon },
  { name: 'Mockups', href: '/app/mockups', icon: PhotoIcon },
  { name: 'Listings', href: '/app/listings', icon: PuzzlePieceIcon },
  { name: 'SEO Optimizer', href: '/app/seo-optimizer', icon: AdjustmentsHorizontalIcon }, // Added SEO Optimizer link
  { name: 'Analytics', href: '/app/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/app/settings', icon: Cog6ToothIcon },
];

const Sidebar: React.FC = () => {
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
        {/* Logout Button or User Info */}
        <button className="group flex w-full items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-dark-card hover:text-dark-text">
          <ArrowLeftOnRectangleIcon className="mr-3 h-6 w-6 flex-shrink-0" aria-hidden="true" />
          Logout
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;

