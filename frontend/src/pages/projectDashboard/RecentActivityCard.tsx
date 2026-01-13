import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Document } from '../../types';

export function RecentActivityCard({ projectId, documents }: { projectId: string; documents: Document[] }) {
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
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Recent Activity</div>
      <div className="mt-2 text-sm text-gray-600">Recently updated project documents.</div>

      <div className="mt-4 divide-y divide-gray-100">
        {recent.length ? (
          recent.map((d) => (
            <div key={d.id} className="py-3 flex items-start justify-between gap-4">
              <div className="min-w-0">
                <div className="text-sm font-medium text-gray-900 truncate">{d.name}</div>
                <div className="text-xs text-gray-600 mt-1">
                  {d.updated_at ? new Date(d.updated_at).toLocaleString() : d.created_at ? new Date(d.created_at).toLocaleString() : '—'}
                </div>
              </div>
              <button
                type="button"
                onClick={() => navigate(`/projects/${projectId}/documents/${d.id}`)}
                className="text-sm text-sky-700 hover:underline flex-shrink-0"
              >
                Open
              </button>
            </div>
          ))
        ) : (
          <div className="py-2 text-sm text-gray-700">No activity yet.</div>
        )}
      </div>
    </div>
  );
}

