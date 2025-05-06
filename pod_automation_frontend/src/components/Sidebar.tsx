import { NavLink } from 'react-router-dom';
import {
  ChartBarIcon,
  Cog6ToothIcon,
  HomeIcon,
  LightBulbIcon,
  PhotoIcon,
  PuzzlePieceIcon,
  SparklesIcon,
  ArrowLeftOnRectangleIcon
} from '@heroicons/react/24/outline';
import Button from './Button';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

const navigation: NavigationItem[] = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Trends', href: '/trends', icon: LightBulbIcon },
  { name: 'AI Studio', href: '/ai-studio', icon: SparklesIcon },
  { name: 'Mockups', href: '/mockups', icon: PhotoIcon },
  { name: 'Listings', href: '/listings', icon: PuzzlePieceIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
];

const Sidebar = () => {
  return (
    <aside className="bg-white dark:bg-dark-bg text-light-text-secondary dark:text-dark-text-secondary w-64 p-4 flex flex-col shadow-lg">
      <div className="mb-8">
        {/* Logo */}
        <div className="text-primary dark:text-primary-light text-2xl font-bold text-center py-4">
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
                ? 'bg-light-bg dark:bg-dark-card text-primary dark:text-primary-light'
                : 'hover:bg-light-bg dark:hover:bg-dark-card hover:text-primary dark:hover:text-primary-light'
              }`
            }
          >
            <item.icon className="mr-3 h-6 w-6 flex-shrink-0" aria-hidden="true" />
            {item.name}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto">
        {/* Logout Button */}
        <Button
          variant="outline"
          className="w-full justify-start"
          icon={ArrowLeftOnRectangleIcon}
        >
          Logout
        </Button>
      </div>
    </aside>
  );
};

export default Sidebar;
