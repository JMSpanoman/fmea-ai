import React from 'react';
import { Button } from './Button';

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  actions,
  className = '',
}) => {
  return (
    <div className={`mb-6 ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-h1 text-text-primary font-bold mb-2">{title}</h1>
          {description && (
            <p className="text-body text-text-secondary">{description}</p>
          )}
        </div>
        {actions && (
          <div className="flex items-center gap-2">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
};

