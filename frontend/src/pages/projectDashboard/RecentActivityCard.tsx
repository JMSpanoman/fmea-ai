import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Document } from '../../types';
import type { LoadAvailability } from './model';

export function RecentActivityCard({
  projectId,
  documents,
  availability,
}: {
  projectId: string;
  documents: Document[];
  availability: LoadAvailability;
}) {
  const navigate = useNavigate();

  const recent = useMemo(() => {
    const list = (documents || []).slice();
    list.sort((a, b) => {
      const ta = a.updated_at || a.created_at || '';
      const tb = b.updated_at || b.created_at || '';
      return tb.localeCompare(ta);
    });
    return list.slice(0, 6);
  }, [documents]);

  return (
    <section className="sr-card p-5 h-full" aria-labelledby="recent-activity-heading">
      <h2 id="recent-activity-heading" className="inline-flex items-center gap-2 text-base font-semibold text-navy">
        <span className="inline-flex w-8 h-8 items-center justify-center rounded-full bg-canvas text-muted" aria-hidden="true">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <circle cx="12" cy="12" r="8" />
            <path d="M12 8v5l3 2" />
          </svg>
        </span>
        Recent activity
      </h2>
      <p className="mt-1 text-sm text-muted">Recently updated project documents.</p>

      <div className="mt-4 divide-y divide-gray-100">
        {availability === 'loading' ? (
          <p className="py-2 text-sm text-muted">Loading activity…</p>
        ) : availability === 'error' ? (
          <p className="py-2 text-sm text-red-700">Activity is unavailable.</p>
        ) : recent.length ? (
          recent.map((d) => (
            <div key={d.id} className="py-3 flex items-start justify-between gap-4">
              <div className="min-w-0">
                <div className="text-sm font-medium text-navy truncate">{d.name}</div>
                <div className="text-xs text-muted mt-1">
                  {d.updated_at
                    ? new Date(d.updated_at).toLocaleString()
                    : d.created_at
                      ? new Date(d.created_at).toLocaleString()
                      : '—'}
                </div>
              </div>
              <button
                type="button"
                onClick={() => navigate(`/projects/${projectId}/documents/${d.id}`)}
                className="text-sm font-medium text-brand hover:underline flex-shrink-0 min-h-control"
              >
                Open
              </button>
            </div>
          ))
        ) : (
          <p className="py-2 text-sm text-muted">No activity yet.</p>
        )}
      </div>
    </section>
  );
}
