import React from 'react';
import type { LoadAvailability, TraceabilityHealthView } from './model';

export function TraceabilityHealthCard({
  health,
  availability,
}: {
  health: TraceabilityHealthView | null;
  availability: LoadAvailability;
}) {
  const statusClass =
    health?.statusKind === 'attention'
      ? 'text-attention'
      : health?.statusKind === 'healthy'
        ? 'text-healthy'
        : 'text-muted';

  return (
    <section className="sr-card p-5 h-full" aria-labelledby="traceability-health-heading">
      <div className="flex items-start justify-between gap-3">
        <h2 id="traceability-health-heading" className="inline-flex items-center gap-2 text-base font-semibold text-navy">
          <span className="inline-flex w-8 h-8 items-center justify-center rounded-full bg-brand-muted text-brand" aria-hidden="true">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <circle cx="6" cy="6" r="2" />
              <circle cx="18" cy="6" r="2" />
              <circle cx="12" cy="18" r="2" />
              <path d="M8 7h8M7 8l4 8M17 8l-4 8" />
            </svg>
          </span>
          Traceability health
        </h2>
        {availability === 'ready' && health ? (
          <span className={`text-sm font-semibold ${statusClass}`}>{health.statusLabel}</span>
        ) : null}
      </div>

      {availability === 'loading' ? (
        <p className="mt-4 text-sm text-muted">Loading traceability health…</p>
      ) : availability === 'error' ? (
        <p className="mt-4 text-sm text-red-700">Traceability health is unavailable.</p>
      ) : !health ? (
        <p className="mt-4 text-sm text-muted">Not evaluated yet.</p>
      ) : (
        <>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="rounded-control bg-canvas border border-gray-100 p-3">
              <p className="text-xs text-muted">Missing links</p>
              <p className="mt-1 text-sm font-semibold text-navy">{health.missingLinksLabel}</p>
            </div>
            <div className="rounded-control bg-canvas border border-gray-100 p-3">
              <p className="text-xs text-muted">Broken links</p>
              <p className="mt-1 text-sm font-semibold text-navy">{health.brokenLinksLabel}</p>
            </div>
          </div>
          <p className="mt-3 text-xs text-muted">{health.supportingText}</p>
        </>
      )}
    </section>
  );
}
