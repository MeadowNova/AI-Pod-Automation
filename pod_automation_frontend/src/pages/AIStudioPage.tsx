import React, { useState } from 'react';
import { SparklesIcon, ChevronDownIcon, TrashIcon, CheckIcon, ArrowPathIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

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

// Placeholder data for generated images
const generatedImagesData = [
  { id: 1, src: '/placeholder-image.png', alt: 'Generated Design 1' },
  { id: 2, src: '/placeholder-image.png', alt: 'Generated Design 2' },
  { id: 3, src: '/placeholder-image.png', alt: 'Generated Design 3' },
  { id: 4, src: '/placeholder-image.png', alt: 'Generated Design 4' },
  { id: 5, src: '/placeholder-image.png', alt: 'Generated Design 5' },
  { id: 6, src: '/placeholder-image.png', alt: 'Generated Design 6' },
];

interface ImageCardProps {
  image: { id: number; src: string; alt: string };
}

const ImageCard: React.FC<ImageCardProps> = ({ image }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className="relative aspect-square bg-gray-200 dark:bg-dark-border rounded-lg overflow-hidden group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <img src={image.src} alt={image.alt} className="w-full h-full object-cover" />
      {isHovered && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center space-x-2 opacity-100 transition-opacity duration-300">
          <Button variant="icon" title="Select" className="bg-white/20 hover:bg-white/40 text-white">
            <CheckIcon className="h-5 w-5" />
          </Button>
          <Button variant="icon" title="Create Variations" className="bg-white/20 hover:bg-white/40 text-white">
            <ArrowPathIcon className="h-5 w-5" />
          </Button>
          <Button variant="icon" title="Delete" className="bg-white/20 hover:bg-white/40 text-white">
            <TrashIcon className="h-5 w-5" />
          </Button>
        </div>
      )}
    </div>
  );
};

const AIStudioPage: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [showHistory, setShowHistory] = useState(false); // State for history tab

  // TODO: Implement actual AI generation logic, state management for config, credits, gallery
  const creditsCost = 1; // Placeholder

  return (
    <div>
      <h1 className="text-2xl font-bold text-light-text dark:text-dark-text mb-6">AI Design Studio</h1>

      {/* Prompt Input */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-light-text dark:text-dark-text mb-2">Generate Designs with AI</h2>
        <textarea
          rows={3}
          placeholder='Enter your design prompt here... (e.g., "A cute cartoon cat wearing sunglasses, synthwave style")'
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text"
        />
      </div>

      {/* Configuration */}
      <div className="mb-6 space-y-4 md:space-y-0 md:flex md:items-center md:space-x-4">
        <h3 className="text-md font-semibold text-light-text dark:text-dark-text">Configuration:</h3>
        {/* Placeholder Dropdowns */}
        <Button variant="outline">
          Style: Vintage <ChevronDownIcon className="h-4 w-4 ml-1" />
        </Button>
        <Button variant="outline">
          Aspect Ratio: 1:1 <ChevronDownIcon className="h-4 w-4 ml-1" />
        </Button>
        <input
          type="text"
          placeholder="Negative Prompt (Optional)"
          value={negativePrompt}
          onChange={(e) => setNegativePrompt(e.target.value)}
          className="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary dark:bg-dark-card dark:border-dark-border dark:text-dark-text text-sm flex-grow md:flex-grow-0"
        />
      </div>

      {/* Generate Button */}
      <div className="mb-8">
        <Button variant="primary">
          <SparklesIcon className="h-5 w-5 mr-1" /> Generate (Cost: {creditsCost} Credit{creditsCost !== 1 ? 's' : ''})
        </Button>
      </div>

      {/* Toggle Buttons for Gallery/History */}
      <div className="mb-4 border-b border-gray-200 dark:border-dark-border">
        <nav className="-mb-px flex space-x-6" aria-label="Tabs">
          <button
            onClick={() => setShowHistory(false)}
            className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm ${!showHistory ? 'border-primary text-primary dark:border-primary-light dark:text-primary-light' : 'border-transparent text-light-text-secondary hover:text-gray-700 hover:border-gray-300 dark:text-dark-text-secondary dark:hover:text-gray-300 dark:hover:border-gray-700'}`}
          >
            Generated Designs
          </button>
          <button
            onClick={() => setShowHistory(true)}
            className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm ${showHistory ? 'border-primary text-primary dark:border-primary-light dark:text-primary-light' : 'border-transparent text-light-text-secondary hover:text-gray-700 hover:border-gray-300 dark:text-dark-text-secondary dark:hover:text-gray-300 dark:hover:border-gray-700'}`}
          >
            Design History / Saved
          </button>
        </nav>
      </div>

      {/* Results Area */} 
      {showHistory ? (
        // Design History Placeholder
        <div className="bg-white dark:bg-dark-bg p-4 rounded-lg shadow">
          <p className="text-center text-light-text-secondary dark:text-dark-text-secondary">Design History/Saved section placeholder.</p>
          {/* TODO: Implement History Table based on wireframe */}
        </div>
      ) : (
        // Generated Designs Gallery
        <div className="bg-white dark:bg-dark-bg p-4 rounded-lg shadow">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
            {generatedImagesData.map(image => (
              <ImageCard key={image.id} image={image} />
            ))}
          </div>
          {/* Pagination Placeholder */}
          <div className="flex justify-center items-center space-x-1">
            <Button variant="outline" className="p-1"><ChevronLeftIcon className="h-5 w-5" /></Button>
            <Button variant="outline" className="p-1 px-3">1</Button>
            <Button variant="outline" className="p-1 px-3">2</Button>
            <Button variant="outline" className="p-1 px-3">3</Button>
            <Button variant="outline" className="p-1"><ChevronRightIcon className="h-5 w-5" /></Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIStudioPage;

