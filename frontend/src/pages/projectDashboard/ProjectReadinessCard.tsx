import React, { useMemo } from 'react';
import type { Document } from '../../types';
import { inferDocStatus } from './DocumentRow';

type Category = 'Risk Management' | 'Design Controls' | 'V&V' | 'Traceability';

const categoryDefs: Array<{ name: Category; types: string[] }> = [
  { name: 'Risk Management', types: ['rmp', 'hazard_analysis', 'fmea', 'risk_controls_doc', 'residual_risk', 'rmf'] },
  { name: 'Design Controls', types: ['design_inputs_doc', 'design_outputs_doc'] },
  { name: 'V&V', types: ['vv_evidence'] },
  { name: 'Traceability', types: ['traceability_matrix'] },
];

function pctFor(types: string[], byType: Record<string, Document>) {
  const statuses = types.map((t) => {
    const d = byType[t];
    return inferDocStatus({ status: d?.status, content: d?.content });
  });
  const approved = statuses.filter((s) => s === 'approved').length;
  return Math.round((approved / statuses.length) * 100);
}

export function ProjectReadinessCard({ documents }: { documents: Document[] }) {
  const byType = useMemo(() => {
    const m: Record<string, Document> = {};
    for (const d of documents || []) if (d?.type) m[d.type] = d;
    return m;
  }, [documents]);

  const breakdown = useMemo(() => {
    return categoryDefs.map((c) => ({
      name: c.name,
      pct: pctFor(c.types, byType),
    }));
  }, [byType]);

  const overall = useMemo(() => {
    if (!breakdown.length) return 0;
    return Math.round(breakdown.reduce((a, b) => a + b.pct, 0) / breakdown.length);
  }, [breakdown]);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Project Readiness</div>
      <div className="mt-2 flex items-end justify-between gap-4">
        <div className="text-3xl font-bold text-gray-900">{overall}%</div>
        <div className="text-sm text-gray-600">Derived from document approval status</div>
      </div>

      <div className="mt-4 space-y-3">
        {breakdown.map((b) => (
          <div key={b.name}>
            <div className="flex items-center justify-between text-xs text-gray-700">
              <span className="font-medium">{b.name}</span>
              <span className="text-gray-600">{b.pct}%</span>
            </div>
            <div className="mt-1 h-2 w-full rounded-full bg-gray-100 overflow-hidden">
              <div className="h-2 bg-emerald-500" style={{ width: `${b.pct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

