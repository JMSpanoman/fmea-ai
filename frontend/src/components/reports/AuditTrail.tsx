import React from 'react';
import { reportUi } from './reportUi';

export type AuditTrailEntry = {
  version: string | number;
  date: string;
  user: string;
  summary: string;
  changeType?: string;
  recordId?: string;
};

type AuditTrailProps = {
  entries: AuditTrailEntry[];
  documentTitle?: string;
};

function changeTypeClass(t: string): string {
  const s = t.toLowerCase();
  if (s.includes('generat') || s.includes('compil'))
    return 'bg-violet-50 text-violet-900 border-violet-200';
  if (s.includes('approv')) return 'bg-emerald-50 text-emerald-800 border-emerald-200';
  if (s.includes('review')) return 'bg-amber-50 text-amber-900 border-amber-200';
  return 'bg-neutral-100 text-neutral-800 border-neutral-200';
}

export function AuditTrail({ entries, documentTitle }: AuditTrailProps) {
  if (!entries.length) {
    return (
      <div className={`${reportUi.emptyDashed} p-5 sm:p-6 print:break-inside-avoid`}>
        <p className={reportUi.titleSm}>No version history loaded</p>
        <p className={`mt-2 ${reportUi.subtitle}`}>
          Versions are loaded from{' '}
          <code className={reportUi.inlineCode}>GET …/documents/…/versions</code>. Open{' '}
          <span className="font-medium text-neutral-800">Versions</span> from the toolbar to refresh, or ensure the document
          has been saved at least once.
        </p>
      </div>
    );
  }

  return (
    <div className={reportUi.stackSection}>
      <div className={`${reportUi.panelMuted} px-4 py-3 print:break-inside-avoid`}>
        <p className={`${reportUi.captionLead} text-neutral-700`}>
          <span className="font-semibold text-neutral-900">Controlled document trail.</span> This list supports review
          readiness; it is not a substitute for your QMS audit log.{documentTitle ? ` Artifact: ${documentTitle}.` : ''}
        </p>
      </div>

      <ol className="relative ms-1 border-s border-neutral-200 pb-2 ps-6 sm:ms-2 sm:ps-8 print:border-neutral-300">
        {entries.map((e, i) => {
          const typeLabel = e.changeType || 'Update';
          return (
            <li key={`${e.recordId ?? ''}-${e.version}-${i}`} className="relative mb-5 last:mb-0 print:break-inside-avoid">
              <span
                className="absolute -start-[22px] mt-1.5 flex h-2.5 w-2.5 rounded-full border-2 border-white bg-neutral-400 ring-1 ring-neutral-300 sm:-start-[25px] print:hidden"
                aria-hidden
              />
              <div className={reportUi.card}>
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-neutral-200 bg-neutral-50/80 px-3 py-2.5 sm:px-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-semibold tabular-nums text-neutral-900">v{e.version}</span>
                    <span
                      className={`rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${changeTypeClass(typeLabel)}`}
                    >
                      {typeLabel}
                    </span>
                  </div>
                  <time className="text-xs font-medium text-neutral-500">{e.date}</time>
                </div>
                <div className="space-y-2 px-3 py-3 sm:px-4">
                  <p className={reportUi.bodyTight}>
                    <span className="font-medium text-neutral-900">Actor:</span> {e.user || 'System'}
                  </p>
                  <p className={reportUi.subtitle}>{e.summary || 'Document updated.'}</p>
                  {e.recordId ? (
                    <p className="font-mono text-[11px] text-neutral-500">Record ID: {e.recordId}</p>
                  ) : null}
                </div>
              </div>
            </li>
          );
        })}
      </ol>

      <p className={`${reportUi.caption} text-neutral-400 print:hidden`}>
        Retention and signature requirements are defined by your quality system. Export HTML/PDF from the toolbar for
        offline archival.
      </p>
    </div>
  );
}
