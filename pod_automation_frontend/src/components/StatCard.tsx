// @ts-ignore
import { ElementType } from 'react';

export interface StatCardProps {
  title: string;
  value: string;
  change?: string;
  icon: ElementType;
}

const StatCard = ({ title, value, change, icon: Icon }: StatCardProps) => {
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

export default StatCard;
