import { ReactNode, HTMLAttributes } from 'react';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  footer?: ReactNode;
  headerAction?: ReactNode;
}

const Card = ({
  children,
  className = '',
  title,
  subtitle,
  footer,
  headerAction,
  ...rest
}: CardProps) => {
  return (
    <div
      className={`bg-white dark:bg-dark-bg rounded-lg shadow overflow-hidden ${className}`}
      {...rest}
    >
      {(title || headerAction) && (
        <div className="px-4 py-3 border-b border-gray-200 dark:border-dark-border flex justify-between items-center">
          <div>
            {title && <h3 className="text-lg font-medium text-light-text dark:text-dark-text">{title}</h3>}
            {subtitle && <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary">{subtitle}</p>}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      <div className="p-4">{children}</div>
      {footer && (
        <div className="px-4 py-3 border-t border-gray-200 dark:border-dark-border bg-gray-50 dark:bg-dark-card">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;
