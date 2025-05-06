import React from 'react';
import { Link } from 'react-router-dom';

// Reusable Button component (assuming it exists or is defined elsewhere)
const Button: React.FC<{ children: React.ReactNode; variant?: 'primary' | 'secondary' | 'outline' | 'link'; className?: string; to?: string }> = ({ children, variant = 'primary', className = '', to }) => {
  const baseStyle = 'px-6 py-2 rounded-md font-medium transition-colors inline-block text-center';
  const primaryStyle = 'bg-primary text-dark-text hover:bg-primary-light';
  const secondaryStyle = 'bg-gray-200 text-light-text hover:bg-gray-300 dark:bg-dark-card dark:text-dark-text dark:hover:bg-dark-border';
  const outlineStyle = 'border border-primary text-primary hover:bg-primary hover:text-dark-text dark:border-primary-light dark:text-primary-light dark:hover:bg-primary-light dark:hover:text-dark-text';
  const linkStyle = 'text-primary hover:underline dark:text-primary-light p-0';

  let styles = `${baseStyle} ${className}`;
  if (variant === 'primary') styles += ` ${primaryStyle}`;
  else if (variant === 'secondary') styles += ` ${secondaryStyle}`;
  else if (variant === 'outline') styles += ` ${outlineStyle}`;
  else if (variant === 'link') styles += ` ${linkStyle}`;

  if (to) {
    return <Link to={to} className={styles}>{children}</Link>;
  }
  return <button className={styles}>{children}</button>;
};

const PricingSnippetSection: React.FC = () => {
  return (
    <section className="py-16 bg-white dark:bg-dark-bg">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-3xl font-bold text-light-text dark:text-dark-text mb-12">
          Find the Perfect Plan
        </h2>
        <div className="flex flex-col md:flex-row justify-center items-stretch gap-8 mb-8">
          {/* Free Plan Card */}
          <div className="border border-gray-200 dark:border-dark-border rounded-lg p-6 md:w-1/3 flex flex-col">
            <h3 className="text-xl font-semibold text-light-text dark:text-dark-text mb-4">Free</h3>
            <p className="text-light-text-secondary dark:text-dark-text-secondary mb-4">Basic Features</p>
            <p className="text-light-text dark:text-dark-text mb-6">Limited AI Credits</p>
            <div className="mt-auto">
              <Button variant="outline" to="/signup" className="w-full">Sign Up Free</Button>
            </div>
          </div>

          {/* Pro Plan Card */}
          <div className="border-2 border-primary dark:border-primary-light rounded-lg p-6 md:w-1/3 flex flex-col relative shadow-lg">
            <span className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-primary text-dark-text px-3 py-1 text-sm font-semibold rounded-full">Most Popular</span>
            <h3 className="text-xl font-semibold text-light-text dark:text-dark-text mb-4">Pro</h3>
            <p className="text-light-text-secondary dark:text-dark-text-secondary mb-4">All Features</p>
            <p className="text-light-text dark:text-dark-text mb-6">Generous AI Credits</p>
            <div className="mt-auto">
              <Button variant="primary" to="/signup" className="w-full">Start Free Trial</Button>
            </div>
          </div>
        </div>
        <Button variant="link" to="/pricing" className="text-lg">
          See Full Pricing &gt;
        </Button>
      </div>
    </section>
  );
};

export default PricingSnippetSection;

