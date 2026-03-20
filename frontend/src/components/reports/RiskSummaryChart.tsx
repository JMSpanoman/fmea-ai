import React from 'react';
import { reportUi } from './reportUi';

export type RiskSummaryChartProps = {
  high: number;
  medium: number;
  low: number;
  variant?: 'fmea' | 'generic';
  footnote?: string;
};

export function RiskSummaryChart({ high, medium, low, variant = 'fmea', footnote }: RiskSummaryChartProps) {
  const total = Math.max(high + medium + low, 1);
  const hasData = high + medium + low > 0;

  const row = (label: string, value: number, barCls: string, labelCls: string) => (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between gap-2 text-sm">
        <span className={`font-medium ${labelCls}`}>{label}</span>
        <span className="tabular-nums font-semibold text-neutral-900">{value}</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-sm border border-neutral-200 bg-neutral-100">
        <div className={`h-full rounded-sm ${barCls}`} style={{ width: `${Math.min(100, (value / total) * 100)}%` }} />
      </div>
    </div>
  );

  const defaultFootnote =
    variant === 'fmea'
      ? 'Distribution by RPN band from parsed preview rows. TODO: bind to project risk matrix thresholds from API.'
      : 'Counts from risk-related columns in the preview (heuristic). TODO: replace with server-computed distribution.';

  return (
    <div className={`${reportUi.panelMuted} p-4 print:break-inside-avoid`}>
      <p className={reportUi.titleSm}>
        {variant === 'fmea' ? 'RPN distribution' : 'Qualitative risk mentions'}
      </p>
      <p className={`mt-1 ${reportUi.captionLead}`}>{footnote ?? defaultFootnote}</p>

      {!hasData ? (
        <div className={`mt-4 ${reportUi.emptyDashed} px-4 py-8 text-center ${reportUi.bodyTight} text-neutral-600`}>
          No band data for this view. Generate the report or widen version scope.
        </div>
      ) : (
        <div className="mt-4 space-y-4">
          {variant === 'fmea' ? (
            <>
              {row('High (RPN ≥ 100)', high, 'bg-red-400/90', 'text-red-900')}
              {row('Medium (50–99)', medium, 'bg-amber-400/90', 'text-amber-900')}
              {row('Low (1–49)', low, 'bg-emerald-500/80', 'text-emerald-900')}
            </>
          ) : (
            <>
              {row('High / critical / unacceptable', high, 'bg-red-400/90', 'text-red-900')}
              {row('Medium / moderate', medium, 'bg-amber-400/90', 'text-amber-900')}
              {row('Low', low, 'bg-emerald-500/80', 'text-emerald-900')}
            </>
          )}
        </div>
      )}
    </div>
  );
}
