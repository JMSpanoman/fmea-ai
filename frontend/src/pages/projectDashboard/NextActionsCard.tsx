import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Document } from '../../types';
import { docTypeById as docsRegistryById } from '../../features/docs/docsRegistry';
import { inferDocStatus, primaryCta } from './DocumentRow';

function daysSince(iso?: string | null) {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  const diff = Date.now() - d.getTime();
  return Math.floor(diff / (1000 * 60 * 60 * 24));
}

function docName(type: string) {
  return docsRegistryById[type]?.name || type;
}

export function NextActionsCard({
  projectId,
  documents,
}: {
  projectId: string;
  documents: Document[];
}) {
  const navigate = useNavigate();
  const actions = useMemo(() => {
    const byType: Record<string, Document> = {};
    for (const d of documents || []) if (d?.type) byType[d.type] = d;

    const required = [
      'rmp',
      'hazard_analysis',
      'fmea',
      'risk_controls_doc',
      'residual_risk',
      'rmf',
      'traceability_matrix',
    ];

    const items: Array<{ label: string; reason: string; cta: string; href: string }> = [];

    for (const t of required) {
      const d = byType[t];
      const status = inferDocStatus({ status: d?.status, content: d?.content });
      if (status === 'not_started') {
        items.push({
          label: `Create ${docName(t)}`,
          reason: 'This required artifact has no content yet.',
          cta: 'Create',
          href: d?.id ? `/projects/${projectId}/documents/${d.id}` : `/projects/${projectId}/documents`,
        });
      }
    }

    // stale draft (>30 days)
    for (const d of documents || []) {
      const status = inferDocStatus({ status: d?.status, content: d?.content });
      if (status !== 'draft') continue;
      const last = d.updated_at || d.created_at;
      const age = daysSince(last);
      if (age !== null && age > 30) {
        items.push({
          label: `${d.name || docName(d.type)}`,
          reason: `Draft has not been updated in ${age} days.`,
          cta: 'Continue',
          href: `/projects/${projectId}/documents/${d.id}`,
        });
      }
    }

    // traceability health placeholder (until real metrics exist)
    // Keep safe: only show if traceability matrix not approved
    const tm = byType['traceability_matrix'];
    if (tm) {
      const st = inferDocStatus({ status: tm.status, content: tm.content });
      if (st !== 'approved') {
        items.push({
          label: `Traceability Matrix`,
          reason: 'Traceability is not approved yet; gaps may exist.',
          cta: primaryCta(st),
          href: `/projects/${projectId}/documents/${tm.id}`,
        });
      }
    }

    return items.slice(0, 6);
  }, [documents, projectId]);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Next Actions</div>
          <div className="mt-2 text-sm text-gray-600">
            Auto-generated checklist based on missing and stale documents.
          </div>
        </div>
        <div className="text-xs text-gray-500">{actions.length ? `${actions.length} items` : ''}</div>
      </div>

      <div className="mt-4">
        {actions.length ? (
          <div className="divide-y divide-gray-100">
            {actions.map((a) => (
              <div key={`${a.label}:${a.href}`} className="py-3 flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="text-sm font-medium text-gray-900">{a.label}</div>
                  <div className="text-sm text-gray-600 mt-1">{a.reason}</div>
                </div>
                <button
                  type="button"
                  onClick={() => navigate(a.href)}
                  className="px-3 py-2 rounded-md text-sm bg-sky-600 text-white hover:bg-sky-700 flex-shrink-0"
                >
                  {a.cta}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-gray-700">No urgent actions detected.</div>
        )}
      </div>
    </div>
  );
}

