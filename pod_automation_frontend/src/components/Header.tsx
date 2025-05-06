import { BellIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import ThemeToggle from './ThemeToggle';
import Button from './Button';

interface HeaderProps {
  title?: string;
}

const Header = ({ title }: HeaderProps) => {
  return (
    <header className="bg-white dark:bg-dark-bg text-light-text-secondary dark:text-dark-text-secondary p-4 shadow-md flex justify-between items-center">
      {/* Page Title */}
      <div>
        {title && <h1 className="text-xl font-semibold text-light-text dark:text-dark-text">{title}</h1>}
      </div>
      <div className="flex items-center space-x-4">
        <ThemeToggle />
        <Button
          variant="icon"
          title="Notifications"
          icon={BellIcon}
        />
        <Button
          variant="outline"
          className="flex items-center space-x-2"
          icon={UserCircleIcon}
        >
          <span>User Profile</span>
        </Button>
      </div>
    </header>
  );
};

export default Header;
