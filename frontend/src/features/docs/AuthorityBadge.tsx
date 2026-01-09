import React from 'react';
import type { DocAuthority } from './docsTypes';

export function AuthorityBadge({ authority }: { authority: DocAuthority }) {
  const cls =
    authority === 'manual'
      ? 'bg-gray-100 text-gray-800'
      : authority === 'ai'
        ? 'bg-purple-100 text-purple-800'
        : 'bg-indigo-100 text-indigo-800';
  const label = authority === 'manual' ? 'Manual' : authority === 'ai' ? 'AI' : 'Hybrid';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {label}
    </span>
  );
}

