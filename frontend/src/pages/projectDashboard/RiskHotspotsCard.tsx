import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Document } from '../../types';
import { inferDocStatus } from './DocumentRow';

function daysSince(iso?: string | null) {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  return Math.floor((Date.now() - d.getTime()) / (1000 * 60 * 60 * 24));
}

type Hotspot = { title: string; reason: string; href: string };

export function RiskHotspotsCard({ projectId, documents }: { projectId: string; documents: Document[] }) {
  const navigate = useNavigate();

  const hotspots = useMemo(() => {
    const list: Hotspot[] = [];
    const byType: Record<string, Document> = {};
    for (const d of documents || []) if (d?.type) byType[d.type] = d;

    // Missing key risk artifacts
    const keyDocs = [
      { type: 'hazard_analysis', title: 'Hazard Analysis' },
      { type: 'fmea', title: 'FMEA' },
      { type: 'risk_controls_doc', title: 'Risk Controls Documentation' },
      { type: 'residual_risk', title: 'Residual Risk Evaluation' },
    ];
    for (const k of keyDocs) {
      const d = byType[k.type];
      const st = inferDocStatus({ status: d?.status, content: d?.content });
      if (st === 'not_started') {
        list.push({
          title: `${k.title} not started`,
          reason: 'A core risk artifact is missing; project readiness is reduced.',
          href: d?.id ? `/projects/${projectId}/documents/${d.id}` : `/projects/${projectId}/documents`,
        });
      }
    }

    // Stale drafts (risk docs)
    for (const d of documents || []) {
      const st = inferDocStatus({ status: d.status, content: d.content });
      if (st !== 'draft') continue;
      const last = d.updated_at || d.created_at;
      const age = daysSince(last);
      if (age !== null && age > 30) {
        list.push({
          title: `Stale draft: ${d.name}`,
          reason: `Draft has not been updated in ${age} days.`,
          href: `/projects/${projectId}/documents/${d.id}`,
        });
      }
    }

    return list.slice(0, 5);
  }, [documents, projectId]);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Risk Hotspots</div>
      <div className="mt-2 text-sm text-gray-600">Top issues inferred from document gaps and staleness.</div>

      <div className="mt-4">
        {hotspots.length ? (
          <div className="space-y-3">
            {hotspots.map((h) => (
              <div key={h.title} className="rounded-md border border-gray-200 p-3">
                <div className="text-sm font-medium text-gray-900">{h.title}</div>
                <div className="text-sm text-gray-600 mt-1">{h.reason}</div>
                <button
                  type="button"
                  onClick={() => navigate(h.href)}
                  className="mt-2 text-sm text-sky-700 hover:underline"
                >
                  Open →
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-gray-700">No hotspots detected.</div>
        )}
      </div>
    </div>
  );
}

