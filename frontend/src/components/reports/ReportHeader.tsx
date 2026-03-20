import React from 'react';
import { RiskBadge, type RiskLevel } from './RiskBadge';
import { reportUi } from './reportUi';

function documentStatusToLevel(status: string): RiskLevel {
  const s = (status || '').toLowerCase();
  if (s === 'approved') return 'low';
  if (s === 'in_review') return 'medium';
  if (s === 'draft') return 'neutral';
  if (s === 'obsolete') return 'high';
  return 'neutral';
}

export type ReportHeaderProps = {
  projectName: string;
  documentTitle: string;
  documentTypeLabel?: string;
  subject: string;
  version: string;
  reportDate: string;
  /** Owner / last editor — TODO: map from dedicated RACI fields when API exposes them */
  owner: string;
  status: string;
};

/**
 * Executive summary header for risk-management documents (ISO 14971–style readability).
 * Print/PDF: flat white surfaces, no decorative gradients.
 */
export function ReportHeader({
  projectName,
  documentTitle,
  documentTypeLabel,
  subject,
  version,
  reportDate,
  owner,
  status,
}: ReportHeaderProps) {
  const displayProject = projectName?.trim() || 'Project';
  const displayTitle = documentTitle?.trim() || 'Risk document';

  const meta = [
    { k: 'Version', v: version },
    { k: 'Report date', v: reportDate },
    { k: 'Owner / editor', v: owner || '—' },
    { k: 'Project', v: displayProject },
    { k: 'Scope', v: subject || '—' },
  ];

  return (
    <header className="overflow-hidden rounded-lg border border-neutral-200 bg-white print:rounded-none print:border-neutral-300 print:shadow-none print:break-inside-avoid">
      <div className="border-b border-neutral-200 bg-white px-4 py-5 sm:px-8 sm:py-7 print:px-0 print:py-4">
        <div className="flex flex-col gap-5 sm:flex-row sm:flex-wrap sm:items-start sm:justify-between">
          <div className="min-w-0 flex-1 space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <p className={reportUi.overline}>Executive summary</p>
              {documentTypeLabel ? (
                <span className="rounded border border-neutral-200 bg-neutral-50 px-2 py-0.5 text-[11px] font-medium text-neutral-700">
                  {documentTypeLabel}
                </span>
              ) : null}
            </div>
            <h1 className="text-xl font-semibold tracking-tight text-neutral-900 sm:text-2xl sm:leading-tight print:text-xl">
              {displayTitle}
            </h1>
            <p className={`max-w-3xl ${reportUi.subtitle}`}>
              <span className="font-medium text-neutral-800">{displayProject}</span>
              {subject ? (
                <>
                  <span className="text-neutral-400"> · </span>
                  {subject}
                </>
              ) : null}
            </p>
          </div>
          <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end print:items-start">
            <RiskBadge level={documentStatusToLevel(status)} label={status || 'Draft'} />
            <p className={`max-w-[16rem] text-left text-xs leading-snug text-neutral-500 sm:text-right print:text-left`}>
              Controlled record — verify version and approval state before formal use.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-px border-t border-neutral-200 bg-neutral-200 sm:grid-cols-2 lg:grid-cols-5 print:grid-cols-5">
        {meta.map((item) => (
          <div key={item.k} className="bg-white px-4 py-3 text-sm text-neutral-800 print:py-2">
            <p className={reportUi.labelUpper}>{item.k}</p>
            <p className="mt-1 font-medium leading-snug text-neutral-900">{item.v}</p>
          </div>
        ))}
      </div>
    </header>
  );
}
