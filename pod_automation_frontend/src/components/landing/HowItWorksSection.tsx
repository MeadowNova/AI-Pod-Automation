import React from 'react';
import { ArrowRightIcon, LightBulbIcon, PhotoIcon, PuzzlePieceIcon, SparklesIcon } from '@heroicons/react/24/outline';

const steps = [
  { name: 'Discover Trends', icon: LightBulbIcon },
  { name: 'AI Creates Designs', icon: SparklesIcon },
  { name: 'Auto-Mockup & Optimize', icon: PhotoIcon },
  { name: 'Publish & Grow', icon: PuzzlePieceIcon },
];

const HowItWorksSection: React.FC = () => {
  return (
    <section className="py-16 bg-light-bg dark:bg-dark-card">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-3xl font-bold text-light-text dark:text-dark-text mb-12">
          Go From Idea to Etsy Listing in Minutes with AI
        </h2>
        <div className="flex flex-col md:flex-row items-center justify-center space-y-8 md:space-y-0 md:space-x-8">
          {steps.map((step, index) => (
            <React.Fragment key={step.name}>
              <div className="flex flex-col items-center text-center max-w-[150px]">
                <div className="bg-primary-light dark:bg-primary rounded-full p-4 mb-3">
                  <step.icon className="h-8 w-8 text-white" aria-hidden="true" />
                </div>
                <p className="font-medium text-light-text dark:text-dark-text">{step.name}</p>
              </div>
              {index < steps.length - 1 && (
                <ArrowRightIcon className="hidden md:block h-6 w-6 text-light-text-secondary dark:text-dark-text-secondary mx-4" />
                // Could add ArrowDownIcon for mobile view if needed
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;

