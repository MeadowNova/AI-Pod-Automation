import React from 'react';
import { Link } from 'react-router-dom';

// Reusable Button component (assuming it exists or is defined elsewhere)
const Button: React.FC<{ children: React.ReactNode; variant?: 'primary' | 'secondary' | 'link'; className?: string; to?: string }> = ({ children, variant = 'primary', className = '', to }) => {
  const baseStyle = 'px-6 py-2 rounded-md font-medium transition-colors inline-block';
  const primaryStyle = 'bg-primary text-dark-text hover:bg-primary-light';
  const secondaryStyle = 'bg-gray-200 text-light-text hover:bg-gray-300 dark:bg-dark-card dark:text-dark-text dark:hover:bg-dark-border';
  const linkStyle = 'text-primary hover:underline dark:text-primary-light p-0'; // Link style button

  let styles = `${baseStyle} ${className}`;
  if (variant === 'primary') styles += ` ${primaryStyle}`;
  else if (variant === 'secondary') styles += ` ${secondaryStyle}`;
  else if (variant === 'link') styles += ` ${linkStyle}`;

  if (to) {
    return <Link to={to} className={styles}>{children}</Link>;
  }
  return <button className={styles}>{children}</button>;
};

interface FeatureSectionProps {
  title: string;
  description: string;
  mockupContent: React.ReactNode;
  learnMoreLink?: string;
  ctaText?: string;
  ctaLink?: string;
  textPosition: 'left' | 'right';
}

const FeatureSection: React.FC<FeatureSectionProps> = ({
  title,
  description,
  mockupContent,
  learnMoreLink = '#',
  ctaText = 'Learn More >',
  ctaLink,
  textPosition,
}) => {
  const textBlock = (
    <div className="md:w-1/2 flex flex-col justify-center">
      <h3 className="text-2xl md:text-3xl font-bold text-light-text dark:text-dark-text mb-4">{title}</h3>
      <p className="text-light-text-secondary dark:text-dark-text-secondary mb-6">{description}</p>
      <Button variant="link" to={ctaLink || learnMoreLink} className="self-start">
        {ctaText}
      </Button>
    </div>
  );

  const mockupBlock = (
    <div className="md:w-1/2 flex items-center justify-center mt-8 md:mt-0">
      <div className="bg-gray-200 dark:bg-dark-border p-4 rounded-lg shadow-lg w-full max-w-md h-64 md:h-80 flex items-center justify-center">
        {/* Placeholder for actual mockup */} 
        {mockupContent || <span className="text-gray-500 dark:text-dark-text-secondary">[Mockup Placeholder]</span>}
      </div>
    </div>
  );

  return (
    <section className="py-16 px-6">
      <div className={`container mx-auto flex flex-col md:flex-row items-center gap-12 ${textPosition === 'right' ? 'md:flex-row-reverse' : ''}`}>
        {textBlock}
        {mockupBlock}
      </div>
    </section>
  );
};

export default FeatureSection;

