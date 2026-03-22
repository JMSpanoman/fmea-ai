import React from 'react';
import { Link } from 'react-router-dom';

export interface PageHeaderBreadcrumb {
  label: string;
  path?: string;
}

interface PageHeaderProps {
  title: string;
  description?: string;
  /** Secondary line under title (e.g. context) */
  subtitle?: string;
  breadcrumbs?: PageHeaderBreadcrumb[];
  actions?: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  subtitle,
  breadcrumbs,
  actions,
  className = '',
}) => {
  return (
    <div className={`mb-6 ${className}`}>
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav className="mb-3 text-sm text-text-secondary" aria-label="Breadcrumb">
          <ol className="flex flex-wrap items-center gap-1">
            {breadcrumbs.map((b, i) => (
              <li key={i} className="flex items-center gap-1">
                {i > 0 && <span className="text-neutral-400">/</span>}
                {b.path ? (
                  <Link to={b.path} className="text-blue-600 hover:underline">
                    {b.label}
                  </Link>
                ) : (
                  <span className="text-neutral-700">{b.label}</span>
                )}
              </li>
            ))}
          </ol>
        </nav>
      )}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-h1 text-text-primary font-bold mb-2">{title}</h1>
          {subtitle && <p className="text-sm text-text-secondary mb-1">{subtitle}</p>}
          {description && (
            <p className="text-body text-text-secondary">{description}</p>
          )}
        </div>
        {actions && (
          <div className="flex flex-shrink-0 flex-wrap items-center gap-2">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
};

