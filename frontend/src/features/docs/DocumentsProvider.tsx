import React, { createContext, useContext, useEffect, useMemo, useReducer, useRef } from 'react';
import { docTypeById, documentTypes, docsGroups } from './docsRegistry';
import type { DocApproval, DocsFilters, DocumentInstance, DocStatus } from './docsTypes';
import {
  approveBackendDocument,
  generateBackendDocument,
  loadConnectedProjectDocInstances,
  saveProjectDocInstances,
  simulateGenerate,
  updateBackendDocument,
} from './docsApi';

type GenerateState = { docTypeId: string; status: 'idle' | 'loading' | 'error'; error?: string };

export interface DocsState {
  projectId: string;
  selectedGroupId: string;
  selectedDocTypeId?: string;
  filters: DocsFilters;
  instancesByTypeId: Record<string, DocumentInstance>;
  generate: GenerateState;
}

type Action =
  | { type: 'SELECT_GROUP'; groupId: string }
  | { type: 'SELECT_DOC'; docTypeId?: string }
  | { type: 'SET_FILTERS'; patch: Partial<DocsFilters> }
  | { type: 'LOAD_INSTANCES'; instances: Record<string, DocumentInstance> }
  | { type: 'UPDATE_CONTENT'; docTypeId: string; content: string }
  | { type: 'UPDATE_STATUS'; docTypeId: string; status: DocStatus }
  | { type: 'ADD_APPROVAL'; docTypeId: string; approval: DocApproval }
  | { type: 'GENERATE_REQUEST'; docTypeId: string }
  | { type: 'GENERATE_SUCCESS'; docTypeId: string; content: string; version: string }
  | { type: 'GENERATE_FAIL'; docTypeId: string; error: string }
  | {
      type: 'APPLY_BACKEND_DOC';
      docTypeId: string;
      patch: Partial<DocumentInstance>;
    }
  | { type: 'RECOMPUTE_IMPACT' };

const defaultFilters: DocsFilters = {
  search: '',
  authority: 'all',
  status: 'all',
  impactedOnly: false,
  requiredOnly: false,
  sort: 'status',
};

function nowIso() {
  return new Date().toISOString();
}

function statusRank(s: DocStatus) {
  if (s === 'not_started') return 0;
  if (s === 'draft') return 1;
  if (s === 'in_review') return 2;
  return 3;
}

function ensureAllInstances(instances: Record<string, DocumentInstance>): Record<string, DocumentInstance> {
  const out: Record<string, DocumentInstance> = { ...instances };
  for (const t of documentTypes) {
    if (!out[t.id]) {
      out[t.id] = {
        docTypeId: t.id,
        status: 'not_started',
        impacted: false,
        approvals: [],
        version: 'v0',
        content: '',
        dependencyStamp: {},
      };
    }
  }
  return out;
}

function computeImpacted(instancesByTypeId: Record<string, DocumentInstance>) {
  const depUpdatedAt: Record<string, string> = {};
  for (const [id, inst] of Object.entries(instancesByTypeId)) {
    if (inst.updatedAt) depUpdatedAt[id] = inst.updatedAt;
  }

  const next: Record<string, DocumentInstance> = { ...instancesByTypeId };
  for (const t of documentTypes) {
    const inst = next[t.id] || { docTypeId: t.id, status: 'not_started' as DocStatus };
    const deps = t.dependencies || [];
    if (deps.length === 0) {
      next[t.id] = { ...inst, impacted: false };
      continue;
    }

    // impacted if any dependency updated after this doc's lastGeneratedAt (or updatedAt if manual)
    const baseline = inst.lastGeneratedAt || inst.updatedAt || '';
    let impacted = false;
    for (const dep of deps) {
      const depTs = depUpdatedAt[dep] || '';
      if (depTs && (!baseline || depTs > baseline)) impacted = true;
    }
    next[t.id] = { ...inst, impacted };
  }
  return next;
}

function reducer(state: DocsState, action: Action): DocsState {
  switch (action.type) {
    case 'SELECT_GROUP':
      return { ...state, selectedGroupId: action.groupId, selectedDocTypeId: undefined };
    case 'SELECT_DOC':
      return { ...state, selectedDocTypeId: action.docTypeId };
    case 'SET_FILTERS':
      return { ...state, filters: { ...state.filters, ...action.patch } };
    case 'LOAD_INSTANCES': {
      const merged = computeImpacted(ensureAllInstances(action.instances));
      return { ...state, instancesByTypeId: merged };
    }
    case 'UPDATE_CONTENT': {
      const prev = state.instancesByTypeId[action.docTypeId] || { docTypeId: action.docTypeId, status: 'draft' as DocStatus };
      const updated = {
        ...prev,
        content: action.content,
        updatedAt: nowIso(),
        status: prev.status === 'not_started' ? ('draft' as DocStatus) : prev.status,
      };
      const next = computeImpacted({ ...state.instancesByTypeId, [action.docTypeId]: updated });
      return { ...state, instancesByTypeId: next };
    }
    case 'UPDATE_STATUS': {
      const prev = state.instancesByTypeId[action.docTypeId] || { docTypeId: action.docTypeId, status: action.status };
      const updated = { ...prev, status: action.status, updatedAt: nowIso() };
      const next = computeImpacted({ ...state.instancesByTypeId, [action.docTypeId]: updated });
      return { ...state, instancesByTypeId: next };
    }
    case 'ADD_APPROVAL': {
      const prev = state.instancesByTypeId[action.docTypeId];
      if (!prev) return state;
      const approvals = [...(prev.approvals || []), action.approval];
      const updated = { ...prev, approvals, status: 'approved' as DocStatus, updatedAt: nowIso() };
      const next = computeImpacted({ ...state.instancesByTypeId, [action.docTypeId]: updated });
      return { ...state, instancesByTypeId: next };
    }
    case 'GENERATE_REQUEST':
      return { ...state, generate: { docTypeId: action.docTypeId, status: 'loading' } };
    case 'GENERATE_SUCCESS': {
      const prev = state.instancesByTypeId[action.docTypeId] || { docTypeId: action.docTypeId, status: 'draft' as DocStatus };
      const updated = {
        ...prev,
        content: action.content,
        version: action.version,
        status: 'draft' as DocStatus,
        updatedAt: nowIso(),
        lastGeneratedAt: nowIso(),
      };
      const next = computeImpacted({ ...state.instancesByTypeId, [action.docTypeId]: updated });
      return { ...state, instancesByTypeId: next, generate: { docTypeId: action.docTypeId, status: 'idle' } };
    }
    case 'GENERATE_FAIL':
      return { ...state, generate: { docTypeId: action.docTypeId, status: 'error', error: action.error } };
    case 'APPLY_BACKEND_DOC': {
      const prev = state.instancesByTypeId[action.docTypeId] || ({ docTypeId: action.docTypeId } as DocumentInstance);
      const updated = { ...prev, ...action.patch };
      const next = computeImpacted({ ...state.instancesByTypeId, [action.docTypeId]: updated });
      return { ...state, instancesByTypeId: next };
    }
    case 'RECOMPUTE_IMPACT':
      return { ...state, instancesByTypeId: computeImpacted(state.instancesByTypeId) };
    default:
      return state;
  }
}

interface DocsContextValue {
  state: DocsState;
  actions: {
    selectGroup: (groupId: string) => void;
    selectDoc: (docTypeId?: string) => void;
    setFilters: (patch: Partial<DocsFilters>) => void;
    updateContent: (docTypeId: string, content: string) => void;
    updateStatus: (docTypeId: string, status: DocStatus) => void;
    approve: (docTypeId: string, approval: DocApproval) => void;
    generate: (docTypeId: string) => Promise<void>;
  };
  derived: {
    groups: typeof docsGroups;
    docTypes: typeof documentTypes;
    docTypeById: typeof docTypeById;
  };
}

const DocsContext = createContext<DocsContextValue | null>(null);

export function DocumentsProvider({
  projectId,
  initialGroupId,
  initialDocTypeId,
  children,
}: {
  projectId: string;
  initialGroupId?: string;
  initialDocTypeId?: string;
  children: React.ReactNode;
}) {
  const init: DocsState = {
    projectId,
    selectedGroupId: initialGroupId || docsGroups[0].id,
    selectedDocTypeId: initialDocTypeId,
    filters: defaultFilters,
    instancesByTypeId: ensureAllInstances({}),
    generate: { docTypeId: '', status: 'idle' },
  };

  const [state, dispatch] = useReducer(reducer, init);
  const saveTimersRef = useRef<Record<string, any>>({});

  // load persisted instances per project
  useEffect(() => {
    let mounted = true;
    loadConnectedProjectDocInstances(projectId).then((instances) => {
      if (!mounted) return;
      dispatch({ type: 'LOAD_INSTANCES', instances });
    });
    return () => {
      mounted = false;
    };
  }, [projectId]);

  // persist changes
  useEffect(() => {
    saveProjectDocInstances(projectId, state.instancesByTypeId);
  }, [projectId, state.instancesByTypeId]);

  // keep in sync when URL changes initial selections
  useEffect(() => {
    if (initialGroupId && initialGroupId !== state.selectedGroupId) {
      dispatch({ type: 'SELECT_GROUP', groupId: initialGroupId });
    }
    if (typeof initialDocTypeId !== 'undefined' && initialDocTypeId !== state.selectedDocTypeId) {
      dispatch({ type: 'SELECT_DOC', docTypeId: initialDocTypeId });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialGroupId, initialDocTypeId]);

  const actions = useMemo(
    () => ({
      selectGroup: (groupId: string) => dispatch({ type: 'SELECT_GROUP', groupId }),
      selectDoc: (docTypeId?: string) => dispatch({ type: 'SELECT_DOC', docTypeId }),
      setFilters: (patch: Partial<DocsFilters>) => dispatch({ type: 'SET_FILTERS', patch }),
      updateContent: (docTypeId: string, content: string) => {
        dispatch({ type: 'UPDATE_CONTENT', docTypeId, content });

        const inst = state.instancesByTypeId[docTypeId];
        if (!inst?.backendDocId) return;

        // Debounced backend save
        const key = `content:${docTypeId}`;
        if (saveTimersRef.current[key]) clearTimeout(saveTimersRef.current[key]);
        saveTimersRef.current[key] = setTimeout(async () => {
          try {
            const updated = await updateBackendDocument(projectId, inst.backendDocId!, { content });
            dispatch({
              type: 'APPLY_BACKEND_DOC',
              docTypeId,
              patch: {
                backendDocId: updated.id,
                status: updated.status === 'approved' ? 'approved' : updated.status === 'in_review' ? 'in_review' : 'draft',
                updatedAt: updated.updated_at || updated.created_at,
                version: `v${updated.version ?? 0}`,
                content: updated.content || '',
              },
            });
          } catch {
            // keep local optimistic content if save fails
          }
        }, 650);
      },
      updateStatus: (docTypeId: string, status: DocStatus) => {
        dispatch({ type: 'UPDATE_STATUS', docTypeId, status });
        const inst = state.instancesByTypeId[docTypeId];
        if (!inst?.backendDocId) return;

        const backendStatus =
          status === 'approved' ? 'approved' : status === 'in_review' ? 'in_review' : status === 'draft' ? 'draft' : 'draft';
        updateBackendDocument(projectId, inst.backendDocId, { status: backendStatus }).then((updated) => {
          dispatch({
            type: 'APPLY_BACKEND_DOC',
            docTypeId,
            patch: {
              backendDocId: updated.id,
              status: updated.status === 'approved' ? 'approved' : updated.status === 'in_review' ? 'in_review' : 'draft',
              updatedAt: updated.updated_at || updated.created_at,
              version: `v${updated.version ?? 0}`,
              content: updated.content || '',
            },
          });
        }).catch(() => {});
      },
      approve: (docTypeId: string, approval: DocApproval) => {
        dispatch({ type: 'ADD_APPROVAL', docTypeId, approval });
        const inst = state.instancesByTypeId[docTypeId];
        if (!inst?.backendDocId) return;
        approveBackendDocument(projectId, inst.backendDocId)
          .then((updated) => {
            dispatch({
              type: 'APPLY_BACKEND_DOC',
              docTypeId,
              patch: {
                backendDocId: updated.id,
                status: updated.status === 'approved' ? 'approved' : updated.status === 'in_review' ? 'in_review' : 'draft',
                updatedAt: updated.updated_at || updated.created_at,
                version: `v${updated.version ?? 0}`,
                content: updated.content || '',
              },
            });
          })
          .catch(() => {});
      },
      generate: async (docTypeId: string) => {
        dispatch({ type: 'GENERATE_REQUEST', docTypeId });
        try {
          const inst = state.instancesByTypeId[docTypeId];
          if (inst?.backendDocId) {
            const res = await generateBackendDocument(projectId, inst.backendDocId);
            dispatch({
              type: 'GENERATE_SUCCESS',
              docTypeId,
              content: res.rendered_html || '',
              version: `v${res.new_version_no ?? 0}`,
            });
            dispatch({
              type: 'APPLY_BACKEND_DOC',
              docTypeId,
              patch: {
                lastGeneratedAt: res.updated_at || nowIso(),
                updatedAt: res.updated_at || nowIso(),
                version: `v${res.new_version_no ?? 0}`,
                content: res.rendered_html || '',
              },
            });
          } else {
            const res = await simulateGenerate(docTypeId);
            dispatch({ type: 'GENERATE_SUCCESS', docTypeId, content: res.content, version: res.version });
          }
        } catch (e: any) {
          dispatch({ type: 'GENERATE_FAIL', docTypeId, error: e?.message || 'Generate failed' });
        }
      },
    }),
    // depend on state for backendDocId and content/status updates
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [projectId, state.instancesByTypeId]
  );

  const value: DocsContextValue = useMemo(
    () => ({
      state,
      actions,
      derived: { groups: docsGroups, docTypes: documentTypes, docTypeById },
    }),
    [state, actions]
  );

  return <DocsContext.Provider value={value}>{children}</DocsContext.Provider>;
}

export function useDocs() {
  const ctx = useContext(DocsContext);
  if (!ctx) throw new Error('useDocs must be used within DocumentsProvider');
  return ctx;
}

export function canGenerate(docTypeId: string) {
  const t = docTypeById[docTypeId];
  // Compile-only docs (no AI) still use the same backend `/generate` endpoint.
  if (['rmf', 'essential_requirements_checklist', 'submission_index', 'audit_package'].includes(docTypeId)) {
    return true;
  }
  return !!t?.supportsAiDraft && (t.authority === 'ai' || t.authority === 'hybrid');
}

export function statusLabel(status: DocStatus) {
  switch (status) {
    case 'not_started':
      return 'Not Started';
    case 'draft':
      return 'Draft';
    case 'in_review':
      return 'In Review';
    case 'approved':
      return 'Approved';
  }
}

export function sortInstances(
  ids: string[],
  instancesByTypeId: Record<string, DocumentInstance>,
  sort: DocsFilters['sort']
) {
  const byName = (a: string, b: string) => (docTypeById[a]?.name || a).localeCompare(docTypeById[b]?.name || b);
  if (sort === 'name') return [...ids].sort(byName);
  if (sort === 'updatedAt') {
    return [...ids].sort((a, b) => {
      const ta = instancesByTypeId[a]?.updatedAt || '';
      const tb = instancesByTypeId[b]?.updatedAt || '';
      if (ta === tb) return byName(a, b);
      return tb.localeCompare(ta);
    });
  }
  // status default
  return [...ids].sort((a, b) => {
    const sa = statusRank(instancesByTypeId[a]?.status || 'not_started');
    const sb = statusRank(instancesByTypeId[b]?.status || 'not_started');
    if (sa === sb) return byName(a, b);
    return sb - sa;
  });
}

