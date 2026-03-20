import React from 'react';
import type { FmeaComplianceSummary } from './reportFmeaCompliance';
import { reportUi } from './reportUi';

type ComplianceChecklistPanelProps = {
  summary: FmeaComplianceSummary;
  totalRows: number;
  filteredVisibleCount?: number;
  riskFilterLabel?: string;
};

function statusIcon(severity: 'pass' | 'warn' | 'fail') {
  const base = 'flex h-8 w-8 shrink-0 items-center justify-center rounded border text-sm font-semibold';
  if (severity === 'pass') {
    return (
      <span className={`${base} border-emerald-200 bg-emerald-50/80 text-emerald-800`} aria-hidden>
        ✓
      </span>
    );
  }
  if (severity === 'fail') {
    return (
      <span className={`${base} border-red-200 bg-red-50/80 text-red-800`} aria-hidden>
        ✕
      </span>
    );
  }
  return (
    <span className={`${base} border-amber-200 bg-amber-50/80 text-amber-900`} aria-hidden>
      !
    </span>
  );
}

export function ComplianceChecklistPanel({
  summary,
  totalRows,
  filteredVisibleCount,
  riskFilterLabel,
}: ComplianceChecklistPanelProps) {
  return (
    <div className={`${reportUi.card} print:break-inside-avoid`}>
      <div className="border-b border-neutral-200 bg-neutral-50/80 px-4 py-3 sm:px-5">
        <h3 className={reportUi.titleSm}>Compliance review checklist</h3>
        <p className={`mt-1 ${reportUi.captionLead} text-neutral-600`}>
          Automated checks against the visible FMEA export. Confirm against your QMS and risk management plan.
          {filteredVisibleCount != null && riskFilterLabel ? (
            <>
              {' '}
              Showing <span className="font-medium text-neutral-800">{filteredVisibleCount}</span> of{' '}
              <span className="font-medium text-neutral-800">{totalRows}</span> rows ({riskFilterLabel}).
            </>
          ) : null}
        </p>
      </div>
      <ul className="divide-y divide-neutral-200">
        {summary.items.map((item) => (
          <li key={item.id} className="flex gap-3 px-4 py-3 sm:px-5">
            <div className="mt-0.5">{statusIcon(item.severity)}</div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold tracking-tight text-neutral-900">{item.label}</p>
              <p className={`mt-1 ${reportUi.subtitle}`}>{item.detail}</p>
            </div>
          </li>
        ))}
      </ul>
      {summary.issueRowIndices.length > 0 ? (
        <div className="border-t border-neutral-200 bg-amber-50/50 px-4 py-3 sm:px-5">
          <p className={`${reportUi.labelUpper} text-amber-900`}>Flagged in table</p>
          <p className="mt-1 text-xs leading-relaxed text-amber-950/90">
            {summary.issueRowIndices.length} row(s) highlighted in the preview (amber = review, red = high RPN without
            mitigation). Scroll the FMEA table to locate them.
          </p>
        </div>
      ) : (
        <div className="border-t border-neutral-200 px-4 py-3 sm:px-5">
          <p className={reportUi.caption}>No row-level flags from current checks.</p>
        </div>
      )}
    </div>
  );
}
