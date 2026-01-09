import React, { useMemo } from 'react';
import { documentTypes, docTypeById } from './docsRegistry';
import { useDocs, sortInstances } from './DocumentsProvider';
import { DocCard } from './DocCard';

export function DocList({
  groupId,
  onNavigate,
}: {
  groupId: string;
  onNavigate: (groupId: string, docTypeId?: string) => void;
}) {
  const { state } = useDocs();

  const ids = useMemo(() => {
    const groupTypes = documentTypes.filter((d) => d.groupId === groupId);
    const filtered = groupTypes.filter((t) => {
      const inst = state.instancesByTypeId[t.id];
      const required = t.required ?? true;
      if (state.filters.requiredOnly && !required) return false;
      if (state.filters.authority !== 'all' && t.authority !== state.filters.authority) return false;
      if (state.filters.status !== 'all' && inst?.status !== state.filters.status) return false;
      if (state.filters.impactedOnly && !inst?.impacted) return false;
      const q = state.filters.search.trim().toLowerCase();
      if (q) {
        const hay = `${t.name} ${t.description}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    return sortInstances(
      filtered.map((t) => t.id),
      state.instancesByTypeId,
      state.filters.sort
    );
  }, [groupId, state.filters, state.instancesByTypeId]);

  if (ids.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 text-sm text-gray-700">
        No documents match your filters.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {ids.map((id) => {
        const docType = docTypeById[id];
        const inst = state.instancesByTypeId[id];
        return (
          <DocCard
            key={id}
            docType={docType}
            instance={inst}
            selected={state.selectedDocTypeId === id}
            onClick={() => onNavigate(groupId, id)}
          />
        );
      })}
    </div>
  );
}

