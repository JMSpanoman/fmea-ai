import React from 'react';
import { reportUi } from './reportUi';

export type SummaryMetric = {
  label: string;
  value: string | number;
  tone?: 'default' | 'high' | 'medium' | 'low';
  hint?: string;
};

const toneAccent = (tone?: SummaryMetric['tone']) =>
  tone === 'high'
    ? 'border-l-red-500'
    : tone === 'medium'
      ? 'border-l-amber-400'
      : tone === 'low'
        ? 'border-l-emerald-600'
        : 'border-l-neutral-300';

/**
 * Executive key metrics — flat, minimal cards; print-safe (no hover / motion).
 * INTEGRATION: Replace client-derived metrics with API summary fields when exposed.
 */
export function SummaryCards({ metrics, title }: { metrics: SummaryMetric[]; title?: string }) {
  return (
    <div className={`${reportUi.stackSection} print:break-inside-avoid`}>
      {title ? (
        <div>
          <h2 className={reportUi.titleSm}>{title}</h2>
          <p className={`mt-1 ${reportUi.captionLead}`}>
            Derived from the current preview where noted; server-side summary fields will replace client parsing when
            exposed by the API.
          </p>
        </div>
      ) : null}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 print:grid-cols-3">
        {metrics.map((m) => (
          <div
            key={m.label}
            className={`rounded-lg border border-neutral-200 bg-white px-4 py-3 print:break-inside-avoid print:border-neutral-300 border-l-4 ${toneAccent(m.tone)}`}
          >
            <p className={reportUi.overline}>{m.label}</p>
            <p className="mt-1.5 text-xl font-semibold tracking-tight text-neutral-900 tabular-nums print:text-lg">
              {m.value}
            </p>
            {m.hint ? <p className={`mt-1.5 ${reportUi.captionLead}`}>{m.hint}</p> : null}
          </div>
        ))}
      </div>
    </div>
  );
}
