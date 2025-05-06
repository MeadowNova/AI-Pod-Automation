import React from 'react';
import type { ReactNode, ElementType } from 'react';
import { Link } from 'react-router-dom';

export interface ButtonProps {
  children?: ReactNode; // Make children optional for icon-only buttons
  variant?: 'primary' | 'secondary' | 'outline' | 'link' | 'icon';
  className?: string;
  to?: string;
  onClick?: () => void;
  key?: string;
  title?: string;
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
  icon?: ElementType;
  isExternal?: boolean;
}

const Button = ({
  children,
  variant = 'primary',
  className = '',
  to,
  onClick,
  title,
  type = 'button',
  disabled = false,
  icon: Icon,
  isExternal = false
}: ButtonProps) => {
  // Base styles for all buttons
  const baseStyle = 'px-4 py-2 rounded-md font-medium transition-colors inline-flex items-center justify-center text-sm';

  // Variant-specific styles
  const primaryStyle = 'bg-primary text-dark-text hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed';
  const secondaryStyle = 'bg-gray-200 text-light-text hover:bg-gray-300 dark:bg-dark-card dark:text-dark-text dark:hover:bg-dark-border disabled:opacity-50 disabled:cursor-not-allowed';
  const outlineStyle = 'border border-gray-300 dark:border-dark-border text-light-text dark:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-border disabled:opacity-50 disabled:cursor-not-allowed';
  const linkStyle = 'text-primary hover:underline dark:text-primary-light p-0 text-sm disabled:opacity-50 disabled:cursor-not-allowed';
  const iconStyle = 'p-1.5 text-light-text-secondary dark:text-dark-text-secondary hover:text-primary dark:hover:text-primary-light disabled:opacity-50 disabled:cursor-not-allowed';

  // Combine styles based on variant
  let styles = variant === 'icon' ? iconStyle : `${baseStyle} ${className}`;
  if (variant === 'primary') styles += ` ${primaryStyle}`;
  else if (variant === 'secondary') styles += ` ${secondaryStyle}`;
  else if (variant === 'outline') styles += ` ${outlineStyle}`;
  else if (variant === 'link') styles += ` ${linkStyle}`;

  // Add icon if provided
  const content = (
    <>
      {Icon && <Icon className={`h-5 w-5 ${children ? 'mr-2' : ''}`} />}
      {children}
    </>
  );

  // Handle different rendering scenarios
  if (to) {
    // External link
    if (isExternal) {
      return (
        <a
          href={to}
          className={styles}
          target="_blank"
          rel="noopener noreferrer"
          title={title}
        >
          {content}
        </a>
      );
    }

    // Internal link using react-router
    try {
      return (
        <Link
          to={to}
          className={styles}
          title={title}
        >
          {content}
        </Link>
      );
    } catch (error) {
      // Fallback to regular anchor if Link fails
      console.warn('Button: Link component failed, falling back to anchor', error);
      return (
        <a
          href={to}
          className={styles}
          title={title}
        >
          {content}
        </a>
      );
    }
  }

  // Regular button
  return (
    <button
      className={styles}
      onClick={onClick}
      type={type}
      disabled={disabled}
      title={title}
    >
      {content}
    </button>
  );
};

export default Button;
