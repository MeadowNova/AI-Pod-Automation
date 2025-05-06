import React, { useState } from 'react';
import { ArrowUpIcon, ArrowDownIcon, ArrowLeftIcon, ArrowRightIcon, PlusIcon, MinusIcon, PencilIcon, TrashIcon, ArrowRightCircleIcon } from '@heroicons/react/24/outline';

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

// Placeholder data
const products = [
  { id: 'tshirt', name: 'T-Shirt' },
  { id: 'mug', name: 'Mug' },
  { id: 'pillow', name: 'Pillow' },
  { id: 'poster', name: 'Poster' },
];

const designs = [
  { id: 1, src: '/placeholder-image.png', alt: 'Design 1' },
  { id: 2, src: '/placeholder-image.png', alt: 'Design 2' },
  { id: 3, src: '/placeholder-image.png', alt: 'Design 3' },
  { id: 4, src: '/placeholder-image.png', alt: 'Design 4' },
];

const generatedMockups = [
  { id: 1, src: '/mockup-thumb1.png', alt: 'Mockup 1', product: 'T-Shirt, Black' },
  { id: 2, src: '/mockup-thumb2.png', alt: 'Mockup 2', product: 'Mug, White' },
  { id: 3, src: '/mockup-thumb3.png', alt: 'Mockup 3', product: 'Pillow, White' },
];

const MockupsPage: React.FC = () => {
  const [selectedProduct, setSelectedProduct] = useState<string | null>('tshirt');
  const [selectedDesign, setSelectedDesign] = useState<number | null>(1);
  const [productColor, setProductColor] = useState('Black');

  // TODO: Implement actual state management for options, preview, adjustments, gallery

  return (
    <div>
      <h1 className="text-2xl font-bold text-light-text dark:text-dark-text mb-6">Mockup Generator</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Column 1: Select Product */}
        <div className="bg-white dark:bg-dark-bg p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-light-text dark:text-dark-text mb-4">1. Select Product</h2>
          <div className="flex flex-wrap gap-2 mb-4">
            {products.map(product => (
              <Button 
                key={product.id} 
                variant={selectedProduct === product.id ? 'primary' : 'outline'} 
                onClick={() => setSelectedProduct(product.id)}
              >
                {product.name}
              </Button>
            ))}
          </div>
          <h3 className="text-md font-semibold text-light-text dark:text-dark-text mb-2">Product Options</h3>
          <div className="space-y-2">
            {/* Placeholder Color Selector */}
            <label className="block text-sm text-light-text-secondary dark:text-dark-text-secondary">
              Color: 
              <select 
                value={productColor}
                onChange={(e) => setProductColor(e.target.value)}
                className="ml-2 p-1 border border-gray-300 rounded-md dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
              >
                <option>Black</option>
                <option>White</option>
                <option>Gray</option>
                <option>Navy</option>
              </select>
            </label>
            {/* Placeholder Size Selector */}
            <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary">Size: All Sizes (Default)</p>
          </div>
        </div>

        {/* Column 2: Choose Design */}
        <div className="bg-white dark:bg-dark-bg p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-light-text dark:text-dark-text mb-4">2. Choose Design</h2>
          <div className="grid grid-cols-3 gap-2 mb-4">
            {designs.map(design => (
              <div 
                key={design.id} 
                className={`aspect-square bg-gray-200 dark:bg-dark-border rounded overflow-hidden cursor-pointer border-2 ${selectedDesign === design.id ? 'border-primary dark:border-primary-light' : 'border-transparent'}`}
                onClick={() => setSelectedDesign(design.id)}
              >
                <img src={design.src} alt={design.alt} className="w-full h-full object-cover" />
              </div>
            ))}
          </div>
          <Button variant="secondary" className="w-full mb-2">Select from AI Studio</Button>
          <Button variant="outline" className="w-full">Upload New Design</Button>
          {selectedDesign && (
            <div className="mt-4">
              <p className="text-sm font-medium text-light-text dark:text-dark-text mb-1">Selected Design:</p>
              <img src={designs.find(d => d.id === selectedDesign)?.src} alt="Selected Design" className="w-16 h-16 object-cover rounded border dark:border-dark-border" />
            </div>
          )}
        </div>

        {/* Column 3: Preview & Adjust */}
        <div className="lg:col-span-3 bg-white dark:bg-dark-bg p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-light-text dark:text-dark-text mb-4">3. Preview & Adjust</h2>
          <div className="flex flex-col items-center">
            {/* Large Mockup Preview Area */}
            <div className="w-full max-w-md h-80 bg-gray-300 dark:bg-dark-border rounded-lg mb-4 flex items-center justify-center">
              <span className="text-gray-500 dark:text-dark-text-secondary">[Large Mockup Preview Placeholder]</span>
              {/* TODO: Display actual mockup based on selectedProduct, selectedDesign, color */}
            </div>
            {/* Adjustment Controls */}
            <div className="flex items-center space-x-2 mb-4">
              <span className="text-sm font-medium">Position:</span>
              <Button variant="icon" title="Move Up"><ArrowUpIcon className="h-5 w-5" /></Button>
              <Button variant="icon" title="Move Down"><ArrowDownIcon className="h-5 w-5" /></Button>
              <Button variant="icon" title="Move Left"><ArrowLeftIcon className="h-5 w-5" /></Button>
              <Button variant="icon" title="Move Right"><ArrowRightIcon className="h-5 w-5" /></Button>
              <span className="text-sm font-medium ml-4">Scale:</span>
              <Button variant="icon" title="Scale Up"><PlusIcon className="h-5 w-5" /></Button>
              <Button variant="icon" title="Scale Down"><MinusIcon className="h-5 w-5" /></Button>
            </div>
            {/* Action Buttons */}
            <div className="flex space-x-4">
              <Button variant="secondary">Save Mockup</Button>
              <Button variant="primary">Proceed to Listing Editor <ArrowRightCircleIcon className="h-5 w-5 ml-1" /></Button>
            </div>
          </div>
        </div>
      </div>

      {/* Generated Mockups Gallery */}
      <div className="bg-white dark:bg-dark-bg p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold text-light-text dark:text-dark-text mb-4">Generated Mockups</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {generatedMockups.map(mockup => (
            <div key={mockup.id} className="relative group">
              <div className="aspect-square bg-gray-200 dark:bg-dark-border rounded-lg overflow-hidden">
                <img src={mockup.src} alt={mockup.alt} className="w-full h-full object-cover" />
              </div>
              <p className="text-xs text-center mt-1 text-light-text-secondary dark:text-dark-text-secondary">{mockup.product}</p>
              {/* Hover Actions */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 flex items-center justify-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <Button variant="icon" title="Edit" className="bg-white/20 hover:bg-white/40 text-white"><PencilIcon className="h-4 w-4" /></Button>
                <Button variant="icon" title="Send to Listing" className="bg-white/20 hover:bg-white/40 text-white"><ArrowRightCircleIcon className="h-4 w-4" /></Button>
                <Button variant="icon" title="Delete" className="bg-white/20 hover:bg-white/40 text-white"><TrashIcon className="h-4 w-4" /></Button>
              </div>
            </div>
          ))}
        </div>
        {/* TODO: Add pagination if needed */}
      </div>
    </div>
  );
};

export default MockupsPage;

