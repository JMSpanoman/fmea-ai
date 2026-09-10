import React from 'react';
import type { LoadAvailability, RiskStatusCounts } from './model';

const TILES: Array<{
  key: keyof Pick<RiskStatusCounts, 'approved' | 'inReview' | 'draft' | 'notStarted'>;
  label: string;
  className: string;
}> = [
  { key: 'approved', label: 'Approved', className: 'bg-healthy-muted text-navy' },
  { key: 'inReview', label: 'In review', className: 'bg-info-muted text-navy' },
  { key: 'draft', label: 'Draft', className: 'bg-draft-muted text-navy' },
  { key: 'notStarted', label: 'Not started', className: 'bg-neutral-100 text-navy' },
];

export function RiskOverviewCard({
  counts,
  availability,
}: {
  counts: RiskStatusCounts | null;
  availability: LoadAvailability;
}) {
  return (
    <section className="sr-card p-5 h-full" aria-labelledby="risk-overview-heading">
      <h2 id="risk-overview-heading" className="inline-flex items-center gap-2 text-base font-semibold text-navy">
        <span className="inline-flex w-8 h-8 items-center justify-center rounded-full bg-brand-muted text-brand" aria-hidden="true">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <path d="M12 3l8 4v6c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V7l8-4z" />
          </svg>
        </span>
        Risk overview
      </h2>

      {availability === 'loading' ? (
        <p className="mt-4 text-sm text-muted">Loading risk overview…</p>
      ) : availability === 'error' ? (
        <p className="mt-4 text-sm text-red-700">Risk overview is unavailable.</p>
      ) : availability === 'empty' || !counts ? (
        <p className="mt-4 text-sm text-muted">No documents available to count.</p>
      ) : (
        <div className="mt-4 grid grid-cols-2 gap-3">
          {TILES.map((tile) => (
            <div key={tile.key} className={`rounded-control p-3 ${tile.className}`}>
              <p className="text-xs text-muted">{tile.label}</p>
              <p className="mt-1 text-2xl font-semibold tabular-nums">{counts[tile.key]}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
