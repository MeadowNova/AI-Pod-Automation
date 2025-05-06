import React from 'react';
import { Link } from 'react-router-dom';

// Reusable Button component (assuming it exists or is defined elsewhere)
const Button: React.FC<{ children: React.ReactNode; variant?: 'primary' | 'secondary' | 'outline' | 'link'; className?: string; to?: string }> = ({ children, variant = 'primary', className = '', to }) => {
  const baseStyle = 'px-6 py-3 rounded-md font-medium transition-colors inline-block text-center text-lg'; // Increased padding and text size
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

const FinalCTASection: React.FC = () => {
  return (
    <section className="py-20 bg-gradient-to-t from-white to-light-bg dark:from-dark-bg dark:to-dark-card">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-light-text dark:text-dark-text mb-8">
          Ready to Supercharge Your Etsy POD Shop?
        </h2>
        <Button variant="primary" to="/signup" className="text-xl px-8 py-4"> {/* Larger button */}
          Start Your Free Trial Today
        </Button>
      </div>
    </section>
  );
};

export default FinalCTASection;

