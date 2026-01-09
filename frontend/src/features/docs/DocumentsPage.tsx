import React, { useEffect, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { docsGroups, groupById } from './docsRegistry';
import { DocumentsProvider, useDocs } from './DocumentsProvider';
import { GroupSidebar } from './GroupSidebar';
import { FiltersBar } from './FiltersBar';
import { DocList } from './DocList';
import { DocDetailPanel } from './DocDetailPanel';

function DocsPageInner() {
  const navigate = useNavigate();
  const { projectId } = useParams();
  const { state, actions } = useDocs();

  const onNavigate = (groupId: string, docTypeId?: string) => {
    if (!projectId) return;
    if (docTypeId) {
      navigate(`/projects/${projectId}/docs/${groupId}/${docTypeId}`);
    } else {
      navigate(`/projects/${projectId}/docs/${groupId}`);
    }
  };

  // Keep selections in sync with current state when user clicks sidebar/list
  useEffect(() => {
    actions.selectGroup(state.selectedGroupId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const groupTitle = useMemo(() => groupById[state.selectedGroupId]?.name || 'Documentation', [state.selectedGroupId]);

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xl font-semibold text-gray-900">Documentation</div>
          <div className="text-sm text-gray-600 mt-1">{groupTitle}</div>
        </div>
      </div>

      <FiltersBar filters={state.filters} onChange={(patch) => actions.setFilters(patch)} />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-3">
          <GroupSidebar onNavigate={onNavigate} />
        </div>

        <div className="col-span-12 lg:col-span-5 space-y-3">
          <DocList groupId={state.selectedGroupId} onNavigate={onNavigate} />
        </div>

        <div className="col-span-12 lg:col-span-4">
          <DocDetailPanel onNavigate={onNavigate} />
        </div>
      </div>
    </div>
  );
}

export default function DocumentsPage() {
  const params = useParams();
  const projectId = params.projectId || '';
  const groupId = params.groupId;
  const docTypeId = params.docTypeId;

  const resolvedGroupId = useMemo(() => {
    if (groupId && docsGroups.some((g) => g.id === groupId)) return groupId;
    return docsGroups[0].id;
  }, [groupId]);

  if (!projectId) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 text-sm text-gray-700">
        Select or create a project to continue.
      </div>
    );
  }

  return (
    <DocumentsProvider projectId={projectId} initialGroupId={resolvedGroupId} initialDocTypeId={docTypeId}>
      <DocsPageInner />
    </DocumentsProvider>
  );
}

