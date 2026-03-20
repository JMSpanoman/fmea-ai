import React from 'react';
import { RiskBadge, rpnToLevel } from './RiskBadge';
import { reportUi } from './reportUi';

export type TopRiskItem = {
  failureMode: string;
  effect: string;
  cause: string;
  rpn: number;
  mitigation: string;
  status: string;
  headline?: string;
};

type TopRisksPanelProps = {
  items: TopRiskItem[];
  docTypeLabel?: string;
  limit?: number;
};

/**
 * Executive-oriented top risks. Data from FMEA row parse or `parseTopRisksFromPreviewHtml` for other exports.
 */
export function TopRisksPanel({ items, docTypeLabel, limit = 6 }: TopRisksPanelProps) {
  const visible = items.slice(0, limit);

  if (!visible.length) {
    return (
      <div className={reportUi.stackSection}>
        <div className={`${reportUi.emptyDashed} p-4 sm:p-5 print:break-inside-avoid`}>
          <p className={reportUi.titleSm}>No ranked risks in this preview</p>
          <p className={`mt-2 ${reportUi.subtitle}`}>
            {docTypeLabel ? (
              <>
                For <span className="font-medium text-neutral-800">{docTypeLabel}</span>, top risks will list here once
                the export contains parseable table rows (or when the summary API is wired).
              </>
            ) : (
              <>Generate the report or switch version scope so the preview includes data rows.</>
            )}
          </p>
          <ul className={`mt-4 list-inside list-disc space-y-1.5 ${reportUi.caption}`}>
            <li>Expected fields: title / hazard, consequence, controls or acceptability, priority signal</li>
            <li>Risk Controls &amp; Benefit–Risk: extend backend export with a summary block or JSON payload</li>
          </ul>
        </div>
        <div className={`${reportUi.card} p-4 print:hidden`}>
          <p className={`${reportUi.labelUpper} text-neutral-400`}>Wire-up checklist</p>
          <ol className="mt-2 list-decimal space-y-1 pl-4 text-xs text-neutral-600">
            <li>Ensure export HTML includes a primary data table with stable column headers.</li>
            <li>
              Map headers in <code className={reportUi.inlineCode}>parseReportPreviewTopRisks.ts</code>.
            </li>
            <li>
              Optional: return <code className={reportUi.inlineCode}>top_risks[]</code> on generate response.
            </li>
          </ol>
        </div>
      </div>
    );
  }

  return (
    <div className={reportUi.stackSection}>
      <p className={reportUi.captionLead}>
        Ranked for this preview only. Confirm against the full report table and controlled risk register before
        decisions.
      </p>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {visible.map((r, idx) => {
          const level = rpnToLevel(r.rpn);
          const rank = idx + 1;
          return (
            <article
              key={`${r.failureMode}-${rank}`}
              className={`${reportUi.card} relative overflow-hidden p-4 sm:p-5 print:break-inside-avoid`}
            >
              <div className="absolute left-0 top-0 h-full w-0.5 bg-neutral-200 print:hidden" aria-hidden />
              <div className="flex flex-wrap items-start justify-between gap-3 pl-0 sm:pl-1">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="inline-flex h-7 min-w-[1.75rem] items-center justify-center rounded border border-neutral-300 bg-neutral-900 text-xs font-semibold text-white">
                      {rank}
                    </span>
                    <RiskBadge level={level} label={`Score ${r.rpn || 0}`} compact />
                    <span className={reportUi.labelUpper}>{r.status}</span>
                  </div>
                  {r.headline ? (
                    <p className={`mt-2 ${reportUi.labelUpper} normal-case tracking-normal text-neutral-600`}>
                      {r.headline}
                    </p>
                  ) : null}
                  <h3 className="mt-1 text-base font-semibold leading-snug text-neutral-900">
                    {r.failureMode || 'Untitled risk'}
                  </h3>
                </div>
              </div>
              <dl className="mt-4 space-y-2 border-t border-neutral-200 pt-4">
                <div>
                  <dt className={reportUi.dt}>Consequence / situation</dt>
                  <dd className={reportUi.dd}>{r.effect || '—'}</dd>
                </div>
                <div>
                  <dt className={reportUi.dt}>Cause / drivers</dt>
                  <dd className={reportUi.dd}>{r.cause || '—'}</dd>
                </div>
                <div>
                  <dt className={reportUi.dt}>Controls / mitigation</dt>
                  <dd className={reportUi.dd}>{r.mitigation || '—'}</dd>
                </div>
              </dl>
            </article>
          );
        })}
      </div>
    </div>
  );
}
