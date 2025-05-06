import type { ElementType } from 'react';
import { ArrowTrendingUpIcon, BanknotesIcon, DocumentDuplicateIcon, CpuChipIcon, CheckCircleIcon, SparklesIcon } from '@heroicons/react/24/outline';
import Button from '../components/Button';
import StatCard from '../components/StatCard';
import Card from '../components/Card';

// Define types for our data
interface QuickAction {
  label: string;
  to: string;
}

interface ActivityItem {
  icon: ElementType;
  text: string;
  time: string;
}

// Placeholder data
const quickActions: QuickAction[] = [
  { label: 'Find New Trends', to: '/trends' },
  { label: 'Create Design', to: '/ai-studio' },
  { label: 'View Listings', to: '/listings' },
];

const recentActivity: ActivityItem[] = [
  { icon: SparklesIcon, text: 'Design "Synth Cat" generated', time: '2h ago' },
  { icon: CheckCircleIcon, text: 'Listing "Cat Tee" published', time: '1d ago' },
  { icon: ArrowTrendingUpIcon, text: 'Trend "Dog Bandana" saved', time: '3d ago' },
];

const DashboardPage = () => {
  const userName = 'User'; // Placeholder

  return (
    <div>
      <h1 className="text-2xl font-bold text-light-text dark:text-dark-text mb-6">
        Welcome Back, {userName}!
      </h1>

      {/* Quick Start / Tip */}
      <Card className="bg-blue-100 dark:bg-blue-900 border border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-200 mb-6" role="alert">
        <div className="flex items-center">
          <strong className="font-bold mr-2">Tip: </strong>
          <span>Use high-contrast keywords found in Trends for your listing titles.</span>
        </div>
      </Card>

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
        <Card
          className="lg:col-span-1"
          title="Quick Actions"
        >
          <div className="space-y-3">
            {quickActions.map(action => (
              <Button key={action.label} variant="secondary" to={action.to} className="w-full text-left">
                {action.label}
              </Button>
            ))}
          </div>
        </Card>

        {/* Recent Activity Card */}
        <Card
          className="lg:col-span-2"
          title="Recent Activity"
          footer={
            <div className="text-right">
              <Button variant="link" to="/activity">View All Activity &gt;</Button>
            </div>
          }
        >
          <ul className="space-y-4">
            {recentActivity.map((activity, index) => (
              <li key={index} className="flex items-center space-x-3">
                <activity.icon className="h-5 w-5 text-light-text-secondary dark:text-dark-text-secondary flex-shrink-0" />
                <span className="flex-1 text-sm text-light-text dark:text-dark-text">{activity.text}</span>
                <span className="text-xs text-light-text-secondary dark:text-dark-text-secondary">{activity.time}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;

