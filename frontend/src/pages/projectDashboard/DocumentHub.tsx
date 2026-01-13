import React, { useMemo } from 'react';
import type { Document } from '../../types';
import { docTypeById as docsRegistryById } from '../../features/docs/docsRegistry';
import { DocumentGroup } from './DocumentGroup';
import { inferDocStatus } from './DocumentRow';

type DocKey =
  | 'rmp'
  | 'rmf'
  | 'hazard_analysis'
  | 'fmea'
  | 'risk_controls_doc'
  | 'residual_risk'
  | 'design_inputs_doc'
  | 'design_outputs_doc'
  | 'vv_evidence'
  | 'traceability_matrix';

const groupDefs: Array<{ title: string; keys: DocKey[] }> = [
  {
    title: 'Risk Management',
    keys: ['rmp', 'hazard_analysis', 'fmea', 'risk_controls_doc', 'residual_risk', 'rmf'],
  },
  {
    title: 'Design Controls',
    keys: ['design_inputs_doc', 'design_outputs_doc'],
  },
  {
    title: 'Verification & Validation',
    keys: ['vv_evidence'],
  },
  {
    title: 'Traceability',
    keys: ['traceability_matrix'],
  },
];

function docDisplayName(type: string) {
  const reg = docsRegistryById[type];
  return reg?.name || type;
}

export function DocumentHub({
  projectId,
  documents,
}: {
  projectId: string;
  documents: Document[];
}) {
  const byType = useMemo(() => {
    const m: Record<string, Document> = {};
    for (const d of documents || []) {
      if (d?.type) m[d.type] = d;
    }
    return m;
  }, [documents]);

  const groups = useMemo(() => {
    return groupDefs.map((g) => {
      const rows = g.keys.map((k) => {
        const d = byType[k];
        const name = d?.name || docDisplayName(k);
        const status = inferDocStatus({ status: d?.status, content: d?.content });
        const updatedAt = d?.updated_at || d?.created_at || null;
        return { docId: d?.id, name, status, updatedAt };
      });
      return { title: g.title, rows };
    });
  }, [byType]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-lg font-semibold text-gray-900">Documents</div>
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {groups.map((g) => (
          <DocumentGroup key={g.title} title={g.title} projectId={projectId} rows={g.rows} />
        ))}
      </div>
    </div>
  );
}

