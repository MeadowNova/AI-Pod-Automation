import React from 'react';
import { ArrowTrendingUpIcon, BanknotesIcon, DocumentDuplicateIcon, CpuChipIcon, CheckCircleIcon, SparklesIcon } from '@heroicons/react/24/outline';
import Button from '../components/Button'; // Import shared Button

interface StatCardProps {
  title: string;
  value: string;
  change?: string;
  icon: React.ElementType;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, icon: Icon }) => {
  const isPositive = change?.startsWith('+');
  const changeColor = isPositive ? 'text-success' : 'text-error'; // Assuming success/error colors defined in Tailwind

  return (
    <div className="bg-white dark:bg-dark-bg p-4 rounded-lg shadow flex items-start space-x-3">
      <div className="bg-primary-light dark:bg-primary p-2 rounded-full">
        <Icon className="h-6 w-6 text-white" />
      </div>
      <div>
        <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary">{title}</p>
        <p className="text-xl font-semibold text-light-text dark:text-dark-text">{value}</p>
        {change && (
          <p className={`text-xs ${changeColor}`}>{change} vs prev 7 days</p>
        )}
      </div>
    </div>
  );
};

// Placeholder data
const quickActions = [
  { label: 'Find New Trends', to: '/dashboard/trends' },
  { label: 'Create Design', to: '/dashboard/ai-studio' },
  { label: 'View Listings', to: '/dashboard/listings' },
  { label: 'SEO Optimizer', to: '/dashboard/seo-optimizer' },
];

const recentActivity = [
  { icon: SparklesIcon, text: 'Design "Synth Cat" generated', time: '2h ago' },
  { icon: CheckCircleIcon, text: 'Listing "Cat Tee" published', time: '1d ago' },
  { icon: ArrowTrendingUpIcon, text: 'Trend "Dog Bandana" saved', time: '3d ago' },
];

const DashboardPage: React.FC = () => {
  const userName = 'User'; // Placeholder

  return (
    <div>
      <h1 className="text-2xl font-bold text-light-text dark:text-dark-text mb-6">
        Welcome Back, {userName}!
      </h1>

      {/* Quick Start / Tip */}
      <div className="bg-blue-100 dark:bg-blue-900 border border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-200 px-4 py-3 rounded-lg relative mb-6" role="alert">
        <strong className="font-bold">Tip: </strong>
        <span className="block sm:inline">Use high-contrast keywords found in Trends for your listing titles.</span>
        {/* TODO: Add dismiss button */}
      </div>

      {/* Shop Overview Stats */}
      <h2 className="text-lg font-semibold text-light-text dark:text-dark-text mb-4">Shop Overview (Last 7 Days)</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="Revenue" value="$123.45" change="+10%" icon={BanknotesIcon} />
        <StatCard title="Orders" value="15" change="-5%" icon={DocumentDuplicateIcon} />
        <StatCard title="Listings Active" value="250" icon={DocumentDuplicateIcon} />
        <StatCard title="AI Credits" value="850" icon={CpuChipIcon} />
      </div>

      {/* Quick Actions & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions Card */}
        <div className="lg:col-span-1 bg-white dark:bg-dark-bg p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-light-text dark:text-dark-text mb-4">Quick Actions</h3>
          <div className="space-y-3">
            {quickActions.map(action => (
              <Button key={action.label} variant="secondary" to={action.to} className="w-full text-left px-4 py-2">
                {action.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Recent Activity Card */}
        <div className="lg:col-span-2 bg-white dark:bg-dark-bg p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-light-text dark:text-dark-text mb-4">Recent Activity</h3>
          <ul className="space-y-4">
            {recentActivity.map((activity, index) => (
              <li key={index} className="flex items-center space-x-3">
                <activity.icon className="h-5 w-5 text-light-text-secondary dark:text-dark-text-secondary flex-shrink-0" />
                <span className="flex-1 text-sm text-light-text dark:text-dark-text">{activity.text}</span>
                <span className="text-xs text-light-text-secondary dark:text-dark-text-secondary">{activity.time}</span>
              </li>
            ))}
          </ul>
          <div className="mt-4 text-right">
            <Button variant="link" to="/dashboard/analytics">View All Activity &gt;</Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;

