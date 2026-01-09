import React from 'react';
import type { DocStatus } from './docsTypes';
import { statusLabel } from './DocumentsProvider';

export function StatusBadge({ status }: { status: DocStatus }) {
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

