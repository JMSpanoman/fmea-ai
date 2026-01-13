import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

export type DocRowStatus = 'not_started' | 'draft' | 'in_review' | 'approved';

export function statusLabel(s: DocRowStatus) {
  if (s === 'not_started') return 'Not started';
  if (s === 'draft') return 'Draft';
  if (s === 'in_review') return 'In review';
  return 'Approved';
}

export function StatusPill({ status }: { status: DocRowStatus }) {
  const cls =
    status === 'approved'
      ? 'bg-green-100 text-green-800'
      : status === 'in_review'
        ? 'bg-yellow-100 text-yellow-800'
        : status === 'draft'
          ? 'bg-blue-100 text-blue-800'
          : 'bg-gray-100 text-gray-800';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {statusLabel(status)}
    </span>
  );
}

export function inferDocStatus(input: { status?: string; content?: string | null }): DocRowStatus {
  const s = (input.status || '').toLowerCase();
  if (s === 'approved') return 'approved';
  if (s === 'in_review') return 'in_review';
  if (!input.content) return 'not_started';
  return 'draft';
}

export function primaryCta(status: DocRowStatus) {
  if (status === 'not_started') return 'Create';
  if (status === 'draft') return 'Continue';
  if (status === 'in_review') return 'Review';
  return 'View';
}

export function DocumentRow({
  projectId,
  title,
  status,
  updatedAt,
  docId,
  detailsHref,
}: {
  projectId: string;
  title: string;
  status: DocRowStatus;
  updatedAt?: string | null;
  docId?: string;
  detailsHref?: string;
}) {
  const navigate = useNavigate();
  const updatedLabel = useMemo(() => {
    if (!updatedAt) return '—';
    try {
      return new Date(updatedAt).toLocaleString();
    } catch {
      return '—';
    }
  }, [updatedAt]);

  const cta = primaryCta(status);
  const canOpen = !!docId;

  return (
    <div className="flex items-center justify-between gap-4 py-2">
      <div className="min-w-0">
        <div className="text-sm font-medium text-gray-900 truncate">{title}</div>
        <div className="mt-1 flex items-center gap-3 text-xs text-gray-600">
          <StatusPill status={status} />
          <span className="whitespace-nowrap">Last updated: {updatedLabel}</span>
          {detailsHref ? (
            <button
              onClick={() => navigate(detailsHref)}
              className="text-xs text-sky-700 hover:underline"
              type="button"
            >
              Details
            </button>
          ) : null}
        </div>
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        <button
          onClick={() => {
            if (canOpen) navigate(`/projects/${projectId}/documents/${docId}`);
            else navigate(`/projects/${projectId}/documents`);
          }}
          className="px-3 py-2 rounded-md text-sm bg-sky-600 text-white hover:bg-sky-700"
          type="button"
        >
          {cta}
        </button>
      </div>
    </div>
  );
}

