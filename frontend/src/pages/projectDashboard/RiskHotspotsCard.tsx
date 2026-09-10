import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Document } from '../../types';
import { inferDocStatus } from './DocumentRow';
import type { LoadAvailability } from './model';

function daysSince(iso?: string | null) {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  return Math.floor((Date.now() - d.getTime()) / (1000 * 60 * 60 * 24));
}

type Hotspot = { title: string; reason: string; href: string };

export function RiskHotspotsCard({
  projectId,
  documents,
  availability,
}: {
  projectId: string;
  documents: Document[];
  availability: LoadAvailability;
}) {
  const navigate = useNavigate();

  const hotspots = useMemo(() => {
    const list: Hotspot[] = [];
    const byType: Record<string, Document> = {};
    for (const d of documents || []) if (d?.type) byType[d.type] = d;

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
    <section className="sr-card p-5 h-full" aria-labelledby="risk-hotspots-heading">
      <h2 id="risk-hotspots-heading" className="inline-flex items-center gap-2 text-base font-semibold text-navy">
        <span className="inline-flex w-8 h-8 items-center justify-center rounded-full bg-canvas text-muted" aria-hidden="true">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <path d="M8 4h8l1 4H7l1-4zM6 8h12v10a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V8z" />
          </svg>
        </span>
        Risk hotspots
      </h2>
      <p className="mt-1 text-sm text-muted">Top issues inferred from document gaps and staleness.</p>

      <div className="mt-4">
        {availability === 'loading' ? (
          <p className="text-sm text-muted">Loading hotspots…</p>
        ) : availability === 'error' ? (
          <p className="text-sm text-red-700">Hotspots are unavailable.</p>
        ) : hotspots.length ? (
          <div className="space-y-3">
            {hotspots.map((h) => (
              <div key={h.title} className="rounded-control border border-gray-200 p-3">
                <div className="text-sm font-medium text-navy">{h.title}</div>
                <div className="text-sm text-muted mt-1">{h.reason}</div>
                <button
                  type="button"
                  onClick={() => navigate(h.href)}
                  className="mt-2 text-sm text-brand hover:underline min-h-control"
                >
                  Open
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted text-center py-6">No hotspots detected.</p>
        )}
      </div>
    </section>
  );
}
