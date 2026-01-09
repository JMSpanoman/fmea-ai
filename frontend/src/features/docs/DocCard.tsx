import React from 'react';
import type { DocumentTypeDef, DocumentInstance } from './docsTypes';
import { AuthorityBadge } from './AuthorityBadge';
import { StatusBadge } from './StatusBadge';

export function DocCard({
  docType,
  instance,
  selected,
  onClick,
}: {
  docType: DocumentTypeDef;
  instance: DocumentInstance;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-lg border p-3 transition ${
        selected ? 'border-primary bg-primary/5' : 'border-gray-200 bg-white hover:bg-gray-50'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <div className="text-sm font-semibold text-gray-900">{docType.name}</div>
            {instance.impacted ? (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                Impacted
              </span>
            ) : null}
          </div>
          <div className="text-xs text-gray-600 mt-1">{docType.description}</div>
        </div>
        <div className="flex items-center gap-2">
          <AuthorityBadge authority={docType.authority} />
          <StatusBadge status={instance.status} />
        </div>
      </div>
      <div className="mt-2 flex items-center justify-between text-xs text-gray-600">
        <div>Version: {instance.version || 'v0'}</div>
        <div>Updated: {instance.updatedAt ? new Date(instance.updatedAt).toLocaleString() : '—'}</div>
      </div>
    </button>
  );
}

