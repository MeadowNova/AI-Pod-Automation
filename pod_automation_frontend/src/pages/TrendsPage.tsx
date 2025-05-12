import React, { useState } from 'react';
import { MagnifyingGlassIcon, AdjustmentsHorizontalIcon, BookmarkIcon, SparklesIcon, TrashIcon, ChevronDownIcon, ChevronUpIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import Button from '../components/Button'; // Import shared Button

// Placeholder data for trends
const trendsData = [
  { id: 1, concept: 'Retro Sunset', trend: 'up', competition: 'Medium', volume: '15k' },
  { id: 2, concept: 'Funny Cat Shirt', trend: 'down', competition: 'Low', volume: '8k' },
  { id: 3, concept: 'Vintage Floral', trend: 'up', competition: 'High', volume: '25k' },
  { id: 4, concept: 'Synthwave Aesthetic', trend: 'up', competition: 'Medium', volume: '12k' },
  { id: 5, concept: 'Minimalist Line Art', trend: 'stable', competition: 'Low', volume: '10k' },
];

// Placeholder data for saved trends
const savedTrendsData = [
  { id: 1, name: 'Retro Sunset', dateSaved: '2025-05-05' },
  { id: 4, name: 'Synthwave Aesthetic', dateSaved: '2025-05-04' },
];

// Mini Trend Graph Placeholder
const MiniTrendGraph: React.FC<{ trend: 'up' | 'down' | 'stable' }> = ({ trend }) => {
  const Icon = trend === 'up' ? ChevronUpIcon : trend === 'down' ? ChevronDownIcon : AdjustmentsHorizontalIcon;
  const color = trend === 'up' ? 'text-success' : trend === 'down' ? 'text-error' : 'text-yellow-500';
  return <Icon className={`h-5 w-5 ${color}`} title={`Trend: ${trend}`} />;
};

const TrendsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showSaved, setShowSaved] = useState(false); // State to toggle between trending and saved

  // TODO: Implement actual search, filtering, sorting, and pagination logic

  return (
    <div>
      <h1 className="text-2xl font-bold text-light-text dark:text-dark-text mb-6">AI Trend Spotting</h1>

      {/* Search and Filters */}
      <div className="mb-6 space-y-4 md:space-y-0 md:flex md:items-center md:justify-between">
        <div className="flex flex-1 mr-4">
          <input
            type="text"
            placeholder="Enter keywords or topics..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-grow p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
          />
          <Button variant="primary" className="rounded-l-none">
            <MagnifyingGlassIcon className="h-5 w-5 mr-1" /> Search
          </Button>
        </div>
        <div className="flex items-center space-x-2">
          {/* Placeholder Filters */}
          <Button variant="outline">
            Category: All <ChevronDownIcon className="h-4 w-4 ml-1" />
          </Button>
          <Button variant="outline">
            Last 30 Days <ChevronDownIcon className="h-4 w-4 ml-1" />
          </Button>
          <Button variant="outline">
            Sort: Trend ▲ <ChevronDownIcon className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </div>

      {/* Toggle Buttons */}
      <div className="mb-4 border-b border-gray-200 dark:border-dark-border">
        <nav className="-mb-px flex space-x-6" aria-label="Tabs">
          <button
            onClick={() => setShowSaved(false)}
            className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm ${!showSaved ? 'border-primary text-primary dark:border-primary-light dark:text-primary-light' : 'border-transparent text-light-text-secondary hover:text-gray-700 hover:border-gray-300 dark:text-dark-text-secondary dark:hover:text-gray-300 dark:hover:border-gray-700'}`}
          >
            Trending Keywords
          </button>
          <button
            onClick={() => setShowSaved(true)}
            className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm ${showSaved ? 'border-primary text-primary dark:border-primary-light dark:text-primary-light' : 'border-transparent text-light-text-secondary hover:text-gray-700 hover:border-gray-300 dark:text-dark-text-secondary dark:hover:text-gray-300 dark:hover:border-gray-700'}`}
          >
            Saved Trends
          </button>
        </nav>
      </div>

      {/* Results Area */}
      <div className="bg-white dark:bg-dark-bg p-4 rounded-lg shadow overflow-x-auto">
        {showSaved ? (
          // Saved Trends Table
          <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-border">
            <thead className="bg-gray-50 dark:bg-dark-card">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Trend Name</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Date Saved</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-dark-bg divide-y divide-gray-200 dark:divide-dark-border">
              {savedTrendsData.map((trend) => (
                <tr key={trend.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-light-text dark:text-dark-text">{trend.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-light-text-secondary dark:text-dark-text-secondary">{trend.dateSaved}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <Button variant="icon" title="Send to AI Studio">
                      <SparklesIcon className="h-5 w-5" />
                    </Button>
                    <Button variant="icon" title="Remove">
                      <TrashIcon className="h-5 w-5 text-error" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          // Trending Keywords Table
          <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-border">
            <thead className="bg-gray-50 dark:bg-dark-card">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Keyword/Concept</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Trend</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Competition</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Volume</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-light-text-secondary dark:text-dark-text-secondary uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-dark-bg divide-y divide-gray-200 dark:divide-dark-border">
              {trendsData.map((trend) => (
                <tr key={trend.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-light-text dark:text-dark-text">{trend.concept}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-light-text-secondary dark:text-dark-text-secondary"><MiniTrendGraph trend={trend.trend as 'up' | 'down' | 'stable'} /></td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-light-text-secondary dark:text-dark-text-secondary">{trend.competition}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-light-text-secondary dark:text-dark-text-secondary">{trend.volume}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <Button variant="icon" title="Save Trend">
                      <BookmarkIcon className="h-5 w-5" />
                    </Button>
                    <Button variant="icon" title="Send to AI Studio">
                      <SparklesIcon className="h-5 w-5" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Pagination Placeholder */}
        {!showSaved && (
          <div className="mt-4 flex justify-center items-center space-x-1">
            <Button variant="outline" className="p-1"><ChevronLeftIcon className="h-5 w-5" /></Button>
            <Button variant="outline" className="p-1 px-3">1</Button>
            <Button variant="outline" className="p-1 px-3">2</Button>
            <Button variant="outline" className="p-1 px-3">3</Button>
            <Button variant="outline" className="p-1"><ChevronRightIcon className="h-5 w-5" /></Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrendsPage;

