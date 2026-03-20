import React from 'react';
import { reportUi } from './reportUi';

export type ReportSectionProps = {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  variant?: 'default' | 'muted';
  id?: string;
  className?: string;
};

/**
 * Reusable section shell for controlled risk reports (FMEA, HA, residual risk, etc.).
 */
export function ReportSection({
  title,
  subtitle,
  children,
  variant = 'default',
  id,
  className = '',
}: ReportSectionProps) {
  const shell =
    variant === 'muted'
      ? `${reportUi.card} bg-neutral-50/80 p-4 sm:p-5 print:border-neutral-300 print:bg-white`
      : `${reportUi.card} p-4 sm:p-5 print:border-neutral-300 print:shadow-none`;

  return (
    <section id={id} className={`${shell} print:break-inside-avoid ${className}`.trim()}>
      <div className="mb-4 border-b border-neutral-200 pb-3 print:mb-3">
        <h2 className={reportUi.titleBase}>{title}</h2>
        {subtitle ? <p className={`mt-1 ${reportUi.subtitle}`}>{subtitle}</p> : null}
      </div>
      {children}
    </section>
  );
}
