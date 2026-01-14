import React, { useMemo } from 'react';
import { DocumentRow, DocRowStatus } from './DocumentRow';

export function percentComplete(statuses: DocRowStatus[]) {
  if (!statuses.length) return 0;
  const approved = statuses.filter((s) => s === 'approved').length;
  return Math.round((approved / statuses.length) * 100);
}

export function ProgressBar({ pct }: { pct: number }) {
  const clamped = Math.max(0, Math.min(100, pct));
  return (
    <div className="h-2 w-full rounded-full bg-gray-100 overflow-hidden">
      <div className="h-2 bg-emerald-500" style={{ width: `${clamped}%` }} />
    </div>
  );
}

export function DocumentGroup({
  title,
  projectId,
  rows,
}: {
  title: string;
  projectId: string;
  rows: Array<{
    docId?: string;
    name: string;
    status: DocRowStatus;
    updatedAt?: string | null;
  }>;
}) {
  const pct = useMemo(() => percentComplete(rows.map((r) => r.status)), [rows]);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm font-semibold text-gray-900">{title}</div>
          <div className="text-xs text-gray-600 mt-1">{pct}% complete</div>
        </div>
        <div className="w-40">
          <ProgressBar pct={pct} />
        </div>
      </div>

      <div className="mt-3 divide-y divide-gray-100">
        {rows.map((r) => (
          <div key={r.docId || r.name} className="py-2">
            <DocumentRow
              projectId={projectId}
              title={r.name}
              status={r.status}
              updatedAt={r.updatedAt}
              docId={r.docId}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

