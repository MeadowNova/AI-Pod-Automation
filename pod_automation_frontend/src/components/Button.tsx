import React from 'react';
import { Link } from 'react-router-dom';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'link' | 'icon';
  className?: string;
  to?: string; // For internal navigation using React Router
  href?: string; // For external links
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  title?: string;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  className = '',
  to,
  href,
  onClick,
  type = 'button',
  title,
  disabled = false,
}) => {
  const baseStyle = 'px-3 py-1.5 rounded-md font-medium transition-colors inline-flex items-center justify-center text-sm disabled:opacity-50 disabled:cursor-not-allowed';
  const primaryStyle = 'bg-primary text-dark-text hover:bg-primary-light';
  const secondaryStyle = 'bg-gray-200 text-light-text hover:bg-gray-300 dark:bg-dark-card dark:text-dark-text dark:hover:bg-dark-border';
  const outlineStyle = 'border border-gray-300 dark:border-dark-border text-light-text dark:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-border';
  const linkStyle = 'text-primary hover:underline dark:text-primary-light p-0 text-sm';
  const iconStyle = 'p-1.5 text-light-text-secondary dark:text-dark-text-secondary hover:text-primary dark:hover:text-primary-light';

  let styles = `${baseStyle} ${className}`;
  if (variant === 'primary') styles += ` ${primaryStyle}`;
  else if (variant === 'secondary') styles += ` ${secondaryStyle}`;
  else if (variant === 'outline') styles += ` ${outlineStyle}`;
  else if (variant === 'link') styles += ` ${linkStyle}`;
  else if (variant === 'icon') styles = `${iconStyle} ${className} ${baseStyle}`.replace('px-3 py-1.5', ''); // Remove default padding for icon if it's already in iconStyle

  if (to) {
    return (
      <Link to={to} className={styles} title={title}>
        {children}
      </Link>
    );
  }

  if (href) {
    return (
      <a href={href} className={styles} title={title} target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    );
  }

  return (
    <button type={type} onClick={onClick} className={styles} title={title} disabled={disabled}>
      {children}
    </button>
  );
};

export default Button;

