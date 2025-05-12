import React, { useState } from 'react';
import { SparklesIcon, CurrencyDollarIcon, EyeIcon, DocumentTextIcon, CloudArrowUpIcon } from '@heroicons/react/24/outline';
import Button from '../components/Button'; // Import shared Button

// Placeholder data
const mockups = [
  { id: 1, src: '/mockup-thumb1.png', alt: 'Mockup 1' },
  { id: 2, src: '/mockup-thumb2.png', alt: 'Mockup 2' },
  { id: 3, src: '/mockup-thumb3.png', alt: 'Mockup 3' },
];

const shippingProfiles = [
  { id: 'profile1', name: 'Standard Shipping' },
  { id: 'profile2', name: 'Free Shipping' },
];

const ListingsPage: React.FC = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [materials, setMaterials] = useState('');
  const [price, setPrice] = useState('');
  const [quantity, setQuantity] = useState('999');
  const [selectedMockup, setSelectedMockup] = useState<number | null>(1);
  const [shippingProfile, setShippingProfile] = useState('profile1');
  const [blueprintId, setBlueprintId] = useState(''); // Placeholder

  const seoScore = 85; // Placeholder

  // TODO: Implement AI suggestions, tag input logic (max 13), form validation, API calls

  return (
    <div>
      <h1 className="text-2xl font-bold text-light-text dark:text-dark-text mb-6">Listing Editor</h1>
      <h2 className="text-lg font-semibold text-light-text dark:text-dark-text mb-4">Create/Edit Etsy Listing</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Column 1 & 2: Listing Details */}
        <div className="lg:col-span-2 bg-white dark:bg-dark-bg p-6 rounded-lg shadow space-y-4">
          <h3 className="text-lg font-semibold text-light-text dark:text-dark-text mb-2">Listing Details</h3>
          
          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">Title</label>
            <div className="flex items-center">
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="flex-grow p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
              />
              <Button variant="secondary" title="Get AI Suggestions" className="rounded-l-none rounded-r-md border-l-0 border-gray-300 dark:border-dark-border px-3 py-1.5">
                <SparklesIcon className="h-5 w-5" />
              </Button>
            </div>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">Description</label>
            <div className="relative">
              <textarea
                id="description"
                rows={5}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
              />
              <Button variant="icon" title="Get AI Suggestions" className="absolute bottom-2 right-2 p-1">
                <SparklesIcon className="h-5 w-5" />
              </Button>
            </div>
          </div>

          {/* Tags */}
          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">Tags (Max 13)</label>
            <div className="flex items-center">
              <input
                type="text"
                id="tags"
                placeholder="Enter tags separated by commas..."
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                className="flex-grow p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
              />
              <Button variant="secondary" title="Get AI Suggestions" className="rounded-l-none rounded-r-md border-l-0 border-gray-300 dark:border-dark-border px-3 py-1.5">
                <SparklesIcon className="h-5 w-5" />
              </Button>
            </div>
            {/* TODO: Add tag count and visual tag input */}
          </div>

          {/* Materials */}
          <div>
            <label htmlFor="materials" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">Materials (Optional)</label>
            <input
              type="text"
              id="materials"
              value={materials}
              onChange={(e) => setMaterials(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
            />
          </div>

          {/* Price & Quantity */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="price" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">Price</label>
              <div className="relative rounded-md shadow-sm">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <CurrencyDollarIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                </div>
                <input
                  type="number"
                  id="price"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  className="block w-full rounded-md border-gray-300 pl-10 p-2 focus:border-primary focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text sm:text-sm"
                  placeholder="0.00"
                />
              </div>
            </div>
            <div>
              <label htmlFor="quantity" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">Quantity</label>
              <input
                type="number"
                id="quantity"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
              />
            </div>
          </div>

          {/* Shipping Profile */}
          <div>
            <label htmlFor="shippingProfile" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">Shipping Profile</label>
            <select
              id="shippingProfile"
              value={shippingProfile}
              onChange={(e) => setShippingProfile(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
            >
              {shippingProfiles.map(profile => (
                <option key={profile.id} value={profile.id}>{profile.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Column 3: Mockups & SEO */}
        <div className="lg:col-span-1 bg-white dark:bg-dark-bg p-6 rounded-lg shadow space-y-4">
          <h3 className="text-lg font-semibold text-light-text dark:text-dark-text mb-2">Mockups</h3>
          <div className="grid grid-cols-3 gap-2 mb-4">
            {mockups.map(mockup => (
              <div 
                key={mockup.id} 
                className={`aspect-square bg-gray-200 dark:bg-dark-border rounded overflow-hidden cursor-pointer border-2 ${selectedMockup === mockup.id ? 'border-primary dark:border-primary-light' : 'border-transparent'}`}
                onClick={() => setSelectedMockup(mockup.id)}
              >
                <img src={mockup.src} alt={mockup.alt} className="w-full h-full object-cover" />
              </div>
            ))}
          </div>
          <Button variant="outline" className="w-full">Add/Manage Mockups</Button>

          <hr className="border-gray-200 dark:border-dark-border my-4" />

          <h3 className="text-lg font-semibold text-light-text dark:text-dark-text mb-2">SEO Score</h3>
          <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-dark-border">
            <div className="bg-success h-2.5 rounded-full" style={{ width: `${seoScore}%` }}></div>
          </div>
          <p className="text-sm text-center text-light-text-secondary dark:text-dark-text-secondary">{seoScore}/100</p>
          <Button variant="link" className="w-full justify-center">View Checklist</Button>

          <hr className="border-gray-200 dark:border-dark-border my-4" />

          <h3 className="text-lg font-semibold text-light-text dark:text-dark-text mb-2">Printify Blueprint</h3>
          {/* Placeholder - Needs actual Blueprint IDs from Printify */}
          <select
            id="blueprintId"
            value={blueprintId}
            onChange={(e) => setBlueprintId(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
          >
            <option value="">Select Blueprint ID...</option>
            <option value="bp123">Blueprint 123 (T-Shirt)</option>
            <option value="bp456">Blueprint 456 (Mug)</option>
          </select>
        </div>
      </div>

      {/* Action Buttons Footer */}
      <div className="flex justify-end space-x-3">
        <Button variant="outline">
          <EyeIcon className="h-5 w-5 mr-1" /> Preview on Etsy
        </Button>
        <Button variant="secondary">
          <DocumentTextIcon className="h-5 w-5 mr-1" /> Save as Draft
        </Button>
        <Button variant="primary">
          <CloudArrowUpIcon className="h-5 w-5 mr-1" /> Publish
        </Button>
      </div>
    </div>
  );
};

export default ListingsPage;

