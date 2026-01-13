import React, { useMemo } from 'react';
import type { Document } from '../../types';
import { inferDocStatus } from './DocumentRow';

export function TraceabilityHealthCard({ documents }: { documents: Document[] }) {
  const tm = useMemo(() => (documents || []).find((d) => d.type === 'traceability_matrix'), [documents]);
  const status = useMemo(() => inferDocStatus({ status: tm?.status, content: tm?.content }), [tm?.status, tm?.content]);

  // Without link-level telemetry available, we keep this honest:
  // - Approved traceability matrix implies "linked" view exists, but we still can't compute %.
  // - Otherwise: Unknown.
  const linkedPct = status === 'approved' ? 'Unknown' : 'Unknown';
  const missingLinks = 'Unknown';
  const brokenLinks = 'Unknown';

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Traceability Health</div>
      <div className="mt-2 flex items-end justify-between">
        <div className="text-2xl font-bold text-gray-900">{linkedPct}</div>
        <div className="text-sm text-gray-600">linked</div>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-3">
        <div className="rounded-md bg-gray-50 border border-gray-100 p-3">
          <div className="text-[11px] text-gray-600">Missing links</div>
          <div className="text-sm font-semibold text-gray-900">{missingLinks}</div>
        </div>
        <div className="rounded-md bg-gray-50 border border-gray-100 p-3">
          <div className="text-[11px] text-gray-600">Broken links</div>
          <div className="text-sm font-semibold text-gray-900">{brokenLinks}</div>
        </div>
      </div>
      <div className="mt-3 text-xs text-gray-600">
        If detailed trace data isn’t available, values remain <b>Unknown</b>.
      </div>
    </div>
  );
}

