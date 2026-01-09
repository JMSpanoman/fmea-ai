import React from 'react';
import type { DocsFilters } from './docsTypes';

export function FiltersBar({
  filters,
  onChange,
}: {
  filters: DocsFilters;
  onChange: (patch: Partial<DocsFilters>) => void;
}) {
  return (
    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between bg-white border border-gray-200 rounded-lg p-3">
      <div className="flex-1 flex items-center gap-2">
        <input
          value={filters.search}
          onChange={(e) => onChange({ search: e.target.value })}
          placeholder="Search documents..."
          className="w-full md:w-80 rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
        <select
          value={filters.authority}
          onChange={(e) => onChange({ authority: e.target.value as any })}
          className="rounded-md border border-gray-300 px-2 py-2 text-sm"
        >
          <option value="all">All Authorities</option>
          <option value="manual">Manual</option>
          <option value="ai">AI</option>
          <option value="hybrid">Hybrid</option>
        </select>
        <select
          value={filters.status}
          onChange={(e) => onChange({ status: e.target.value as any })}
          className="rounded-md border border-gray-300 px-2 py-2 text-sm"
        >
          <option value="all">All Statuses</option>
          <option value="not_started">Not Started</option>
          <option value="draft">Draft</option>
          <option value="in_review">In Review</option>
          <option value="approved">Approved</option>
        </select>
      </div>

      <div className="flex items-center gap-3">
        <label className="inline-flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={filters.impactedOnly}
            onChange={(e) => onChange({ impactedOnly: e.target.checked })}
          />
          Impacted only
        </label>
        <label className="inline-flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={filters.requiredOnly}
            onChange={(e) => onChange({ requiredOnly: e.target.checked })}
          />
          Required only
        </label>
        <select
          value={filters.sort}
          onChange={(e) => onChange({ sort: e.target.value as any })}
          className="rounded-md border border-gray-300 px-2 py-2 text-sm"
        >
          <option value="status">Sort: Status</option>
          <option value="updatedAt">Sort: Updated</option>
          <option value="name">Sort: Name</option>
        </select>
      </div>
    </div>
  );
}

