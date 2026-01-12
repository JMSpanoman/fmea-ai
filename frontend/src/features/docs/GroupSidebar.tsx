import React, { useMemo } from 'react';
import { docsGroups, documentTypes } from './docsRegistry';
import { useDocs } from './DocumentsProvider';

function groupCounts(groupId: string, instancesByTypeId: any) {
  const types = documentTypes.filter((d) => d.groupId === groupId);
  const total = types.length;
  let approved = 0;
  for (const t of types) {
    if (instancesByTypeId[t.id]?.status === 'approved') approved += 1;
  }
  return { total, approved };
}

export function GroupSidebar({
  onNavigate,
}: {
  onNavigate: (groupId: string, docTypeId?: string) => void;
}) {
  const { state } = useDocs();
  const items = useMemo(() => {
    return docsGroups.map((g) => {
      const c = groupCounts(g.id, state.instancesByTypeId);
      return { ...g, ...c };
    });
  }, [state.instancesByTypeId]);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3">
      <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Groups</div>
      <div className="space-y-1">
        {items.map((g) => {
          const active = state.selectedGroupId === g.id;
          return (
            <button
              key={g.id}
              onClick={() => onNavigate(g.id)}
              className={`w-full text-left px-3 py-2 rounded-md transition ${
                active ? 'bg-primary/10 text-primary' : 'hover:bg-gray-50 text-gray-800'
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="text-sm font-medium">{g.name}</div>
                <div className="text-xs text-gray-600 text-right whitespace-nowrap flex-shrink-0">
                  {g.approved}/{g.total} approved
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

