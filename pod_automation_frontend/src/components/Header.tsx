import React from 'react';
import { Link } from 'react-router-dom';
import { BellIcon, UserCircleIcon } from '@heroicons/react/24/outline'; // Using Heroicons as per style guide

const Header: React.FC = () => {
  return (
    <header className="bg-dark-bg text-dark-text-secondary p-4 shadow-md flex justify-between items-center">
      {/* Logo Placeholder - Assuming it's part of the Sidebar or main layout */}
      <div>
        <Link to="/" className="text-dark-text hover:text-primary-light">Home</Link>
      </div>
      <div className="flex items-center space-x-4">
        <button className="hover:text-dark-text">
          <BellIcon className="h-6 w-6" />
        </button>
        <button className="flex items-center space-x-2 hover:text-dark-text">
          <UserCircleIcon className="h-6 w-6" />
          <span>User Profile</span> {/* Replace with actual user name/dropdown */}
        </button>
      </div>
    </header>
  );
};

export default Header;
