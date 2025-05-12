import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { BanknotesIcon, ShoppingCartIcon, ScaleIcon, PresentationChartLineIcon, ChevronDownIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

// Reusable Button component (assuming it exists or is defined elsewhere)
const Button: React.FC<{ children: React.ReactNode; variant?: 'primary' | 'secondary' | 'outline' | 'link' | 'icon'; className?: string; onClick?: () => void; title?: string }> = ({ children, variant = 'primary', className = '', onClick, title }) => {
  const baseStyle = 'px-3 py-1.5 rounded-md font-medium transition-colors inline-flex items-center justify-center text-sm';
  const primaryStyle = 'bg-primary text-dark-text hover:bg-primary-light';
  const secondaryStyle = 'bg-gray-200 text-light-text hover:bg-gray-300 dark:bg-dark-card dark:text-dark-text dark:hover:bg-dark-border';
  const outlineStyle = 'border border-gray-300 dark:border-dark-border text-light-text dark:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-border';
  const linkStyle = 'text-primary hover:underline dark:text-primary-light p-0 text-sm';
  const iconStyle = 'p-1.5 text-light-text-secondary dark:text-dark-text-secondary hover:text-primary dark:hover:text-primary-light'; // Style for icon-only buttons

  let styles = `${baseStyle} ${className}`;
  if (variant === 'primary') styles += ` ${primaryStyle}`;
  else if (variant === 'secondary') styles += ` ${secondaryStyle}`;
  else if (variant === 'outline') styles += ` ${outlineStyle}`;
  else if (variant === 'link') styles += ` ${linkStyle}`;
  else if (variant === 'icon') styles = `${iconStyle} ${className}`; // Use specific style for icon buttons

  return <button onClick={onClick} className={styles} title={title}>{children}</button>;
};

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
          <p className={`text-xs ${changeColor}`}>{change} vs prev period</p>
        )}
      </div>
    </div>
  );
};

// Placeholder data for sales trend chart
const salesData = [
  { name: 'Day 1', Sales: 40 },
  { name: 'Day 5', Sales: 30 },
  { name: 'Day 10', Sales: 20 },
  { name: 'Day 15', Sales: 27 },
  { name: 'Day 20', Sales: 18 },
  { name: 'Day 25', Sales: 23 },
  { name: 'Day 30', Sales: 34 },
];

// Placeholder data for top performing listings
const topListingsData = [
  { id: 1, thumbnail: '/mockup-thumb1.png', title: 'Synthwave Cat T-Shirt', views: '1.2k', orders: 50, revenue: '$550.00' },
  { id: 2, thumbnail: '/mockup-thumb3.png', title: 'Vintage Floral Pillow', views: '800', orders: 35, revenue: '$420.50' },
  { id: 3, thumbnail: '/placeholder-image.png', title: 'Funny Dog Bandana', views: '1.5k', orders: 65, revenue: '$390.00' },
  { id: 4, thumbnail: '/mockup-thumb2.png', title: 'Minimalist Line Art Mug', views: '600', orders: 25, revenue: '$300.00' },
];

const AnalyticsPage: React.FC = () => {
  // Removed unused setDateRange
  const [dateRange] = useState('Last 30 Days');

  // TODO: Implement date range picker logic, actual data fetching

  return (
    <div>
      <h1 className="text-2xl font-bold text-light-text dark:text-dark-text mb-6">Analytics Dashboard</h1>

      {/* Date Range Selector */}
      <div className="mb-6 flex items-center space-x-2">
        <span className="text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">Date Range:</span>
        {/* Placeholder Dropdown */}
        <Button variant="outline">
          {dateRange} <ChevronDownIcon className="h-4 w-4 ml-1" />
        </Button>
        {/* TODO: Add Custom Range Picker */}
        {/* <Button variant="outline">Custom Range</Button> */}
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Sales" value="$1234.56" change="+12%" icon={BanknotesIcon} />
        <StatCard title="Total Orders" value="123" change="+8%" icon={ShoppingCartIcon} />
        <StatCard title="Avg Order Value" value="$10.04" change="+3%" icon={ScaleIcon} />
        <StatCard title="Conversion Rate" value="2.5%" change="+0.2%" icon={PresentationChartLineIcon} />
      </div>

      {/* Sales Trend Chart */}
      <div className="bg-white dark:bg-dark-bg p-4 rounded-lg shadow mb-8">
        <h2 className="text-lg font-semibold text-light-text dark:text-dark-text mb-4">Sales Trend</h2>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <LineChart
              data={salesData}
              margin={{ top: 5, right: 20, left: -10, bottom: 5 }}
            >
              {/* Use CSS variables for stroke */}
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid-stroke)" />
              {/* Use CSS variables for tick fill */}
              <XAxis dataKey="name" tick={{ fill: 'var(--chart-tick-fill)', fontSize: 12 }} />
              <YAxis tick={{ fill: 'var(--chart-tick-fill)', fontSize: 12 }} />
              {/* Use CSS variables for Tooltip styles */}
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'var(--chart-tooltip-bg)', 
                  border: '1px solid var(--chart-tooltip-border)', 
                  borderRadius: '4px' 
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Line type="monotone" dataKey="Sales" stroke="#8884d8" activeDot={{ r: 8 }} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Performing Listings Table */}
      <div className="bg-white dark:bg-dark-bg p-4 rounded-lg shadow overflow-x-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-light-text dark:text-dark-text">Top Performing Listings</h2>
          {/* Placeholder Sort Dropdown */}
          <Button variant="outline">
            Sort by: Revenue <ChevronDownIcon className="h-4 w-4 ml-1" />
          </Button>
        </div>
        <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-border">
          <thead className="bg-gray-50 dark:bg-dark-card">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Listing</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Views</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Orders</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Revenue</th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-dark-bg divide-y divide-gray-200 dark:divide-dark-border">
            {topListingsData.map((listing) => (
              <tr key={listing.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10">
                      <img className="h-10 w-10 rounded-md object-cover" src={listing.thumbnail} alt="" />
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-light-text dark:text-dark-text truncate w-48" title={listing.title}>{listing.title}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-light-text-secondary dark:text-dark-text-secondary">{listing.views}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-light-text-secondary dark:text-dark-text-secondary">{listing.orders}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-light-text dark:text-dark-text">{listing.revenue}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {/* Pagination Placeholder */}
        <div className="mt-4 flex justify-center items-center space-x-1">
          <Button variant="outline" className="p-1"><ChevronLeftIcon className="h-5 w-5" /></Button>
          <Button variant="outline" className="p-1 px-3">1</Button>
          <Button variant="outline" className="p-1 px-3">2</Button>
          <Button variant="outline" className="p-1 px-3">3</Button>
          <Button variant="outline" className="p-1"><ChevronRightIcon className="h-5 w-5" /></Button>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;

