import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import authService from '../services/authService';
import { documentsApi } from '../services/apiPhase3';
import api from '../axios';
import type { Document } from '../types';
import { docTypeById as docsRegistryById } from '../features/docs/docsRegistry';
import { KpiCardsRow, KpiCard, MiniBreakdown } from './projectDashboard/KpiCardsRow';
import { NextActionsCard } from './projectDashboard/NextActionsCard';
import { DocumentHub } from './projectDashboard/DocumentHub';
import { inferDocStatus } from './projectDashboard/DocumentRow';
import { ProjectReadinessCard } from './projectDashboard/ProjectReadinessCard';
import { TraceabilityHealthCard } from './projectDashboard/TraceabilityHealthCard';
import { RiskHotspotsCard } from './projectDashboard/RiskHotspotsCard';
import { RecentActivityCard } from './projectDashboard/RecentActivityCard';
import { projectGenerateAiDraftsFromSetupApi } from '../services/apiPhase1';

type LoadState = 'idle' | 'loading' | 'error' | 'ready';

const setupDraftDocTypes = new Set([
  'rmp',
  'hazard_analysis',
  'fmea',
  'design_inputs_doc',
  'design_outputs_doc',
  'vv_plan',
  'vv_evidence',
  'traceability_matrix',
  'residual_risk',
  'risk_controls_doc',
]);

function normalizeContent(s: string | null | undefined) {
  return String(s || '').trim().toLowerCase();
}

function isStarterOrEmptyDoc(doc?: Document | null) {
  if (!doc) return true;
  const s = normalizeContent(doc.content);
  if (!s) return true;
  const status = String(doc.status || '').trim().toLowerCase();
  if (status === 'not started' || status === 'not_started' || status === 'not-started') return true;
  if (s.includes('hazard analysis export configuration starter')) return true;
  if (s.startsWith('fmea starter')) return true;
  if (s.startsWith('design inputs documentation starter')) return true;
  if (s.startsWith('rmp starter')) return true;
  return false;
}

function isGeneratedFromProjectSetup(doc?: Document | null) {
  if (!doc?.content) return false;
  if (!setupDraftDocTypes.has(String(doc.type || ''))) return false;
  const s = normalizeContent(doc.content);
  // RMP/Hazard Analysis/Design Inputs include explicit deterministic header
  if (s.includes('generated deterministically from projectprofile + components')) return true;
  // FMEA draft uses a slightly different deterministic marker set
  if (s.includes('fmea — draft') && s.includes('project id:') && s.includes('severity/occurrence/detection') && s.includes('[draft]'))
    return true;
  return false;
}

const typeLabel = (t: string) => {
  const reg = docsRegistryById[t];
  if (reg?.name) return reg.name;
  switch (t) {
    case 'rmp':
      return 'RMP';
    case 'rmf':
      return 'RMF/RMR';
    case 'hazard_analysis':
      return 'Hazard Analysis';
    case 'residual_risk':
      return 'Residual Risk';
    case 'risk_controls_doc':
      return 'Risk Controls Doc';
    case 'fmea':
      return 'FMEA';
    case 'design_inputs_doc':
      return 'Design Inputs';
    case 'design_outputs_doc':
      return 'Design Outputs';
    case 'vv_evidence':
      return 'V&V Evidence';
    case 'traceability_matrix':
      return 'Traceability Matrix';
    default:
      return t;
  }
};

function computeReadiness(docs: Document[]) {
  if (!docs?.length) return { pct: 0, breakdown: [] as Array<{ label: string; value: string }> };
  const statuses = docs.map((d) => inferDocStatus({ status: d.status, content: d.content }));
  const approved = statuses.filter((s) => s === 'approved').length;
  const pct = Math.round((approved / statuses.length) * 100);
  const breakdown = [
    { label: 'Approved', value: String(approved) },
    { label: 'In review', value: String(statuses.filter((s) => s === 'in_review').length) },
    { label: 'Draft', value: String(statuses.filter((s) => s === 'draft').length) },
    { label: 'Not started', value: String(statuses.filter((s) => s === 'not_started').length) },
  ];
  return { pct, breakdown };
}

export default function ProjectDashboardPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { currentProject, setCurrentProject, clearCurrentProject } = useProject();

  const [state, setState] = useState<LoadState>('idle');
  const [error, setError] = useState<string>('');
  const [actionError, setActionError] = useState<string>('');
  const [actionInfo, setActionInfo] = useState<string>('');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [openingWizard, setOpeningWizard] = useState(false);
  const [setupIncomplete, setSetupIncomplete] = useState(false);
  const [setupExists, setSetupExists] = useState(false);
  const [generatingInitialDrafts, setGeneratingInitialDrafts] = useState(false);
  const [generatingAiFmea, setGeneratingAiFmea] = useState(false);

  const finalProjectId = projectId || '';

  const setupSkippedKey = useMemo(() => (finalProjectId ? `setup_skipped_${finalProjectId}` : ''), [finalProjectId]);

  const projectName = useMemo(() => {
    if (currentProject?.id === finalProjectId) return currentProject.name;
    return 'Project';
  }, [currentProject, finalProjectId]);

  const readiness = useMemo(() => computeReadiness(documents), [documents]);

  const checkSetup = async () => {
    if (!finalProjectId) return;

    const skipped = setupSkippedKey ? localStorage.getItem(setupSkippedKey) === '1' : false;

    // If explicitly skipped, treat setup as incomplete without extra API calls.
    if (skipped) {
      setSetupIncomplete(true);
      setSetupExists(true);
      return;
    }

    // Setup complete rules:
    // - profile.intended_use present
    // - components count >= 1
    let hasIntendedUse = false;
    let hasComponents = false;
    let hasAnyProfile = false;

    try {
      const profileRes = await api.get(`/projects/${finalProjectId}/profile`);
      const p = profileRes.data || {};
      hasAnyProfile = true;
      hasIntendedUse = Boolean(String(p.intended_use || '').trim());
    } catch {
      hasIntendedUse = false;
      hasAnyProfile = false;
    }

    try {
      const compsRes = await api.get(`/projects/${finalProjectId}/components`);
      const comps = Array.isArray(compsRes.data) ? compsRes.data : [];
      hasComponents = comps.length > 0;
    } catch {
      hasComponents = false;
    }

    setSetupIncomplete(!(hasIntendedUse && hasComponents));
    setSetupExists(Boolean(hasAnyProfile || hasComponents));
  };

  const load = async () => {
    if (!finalProjectId) return;
    setState('loading');
    setError('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }

      // If context isn't set (or mismatched), hydrate it from /projects
      if (!currentProject || currentProject.id !== finalProjectId) {
        try {
          const res = await api.get('/projects');
          const p = (res.data as any[]).find((x) => x.id === finalProjectId);
          if (p) setCurrentProject(p);
        } catch {
          // non-fatal for docs listing
        }
      }

      const docs = await documentsApi.getAll(finalProjectId);
      setDocuments(Array.isArray(docs) ? docs : []);
      setState('ready');
      // Non-blocking: compute setup completeness banner
      checkSetup();
    } catch (e: any) {
      const status = e?.response?.status;
      const detail = e?.response?.data?.detail;
      // Self-heal: if a stale/foreign projectId is saved in localStorage, clear it and redirect.
      if (status === 404 && String(detail || '').toLowerCase().includes('project not found')) {
        try {
          clearCurrentProject();
        } catch {
          // ignore
        }
        navigate('/projects', { replace: true });
        return;
      }
      const msg =
        e?.message ||
        e?.response?.data?.detail ||
        'Failed to load project documents';
      setError(String(msg));
      setState('error');
    }
  };

  useEffect(() => {
    if (!finalProjectId) return;
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finalProjectId, location.key]);

  // Also refresh when documents are created/updated elsewhere and when the tab regains focus.
  const loadingRef = useRef(false);
  useEffect(() => {
    if (!finalProjectId) return;

    const safeLoad = () => {
      if (loadingRef.current) return;
      loadingRef.current = true;
      Promise.resolve(load()).finally(() => {
        loadingRef.current = false;
      });
    };

    const onDocsChanged = (ev: any) => {
      const pid = ev?.detail?.projectId;
      if (!pid || pid === finalProjectId) safeLoad();
    };

    const onFocus = () => safeLoad();
    const onVis = () => {
      if (document.visibilityState === 'visible') safeLoad();
    };

    window.addEventListener('project-documents-changed', onDocsChanged as any);
    window.addEventListener('focus', onFocus);
    document.addEventListener('visibilitychange', onVis);
    return () => {
      window.removeEventListener('project-documents-changed', onDocsChanged as any);
      window.removeEventListener('focus', onFocus);
      document.removeEventListener('visibilitychange', onVis);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finalProjectId]);

  const openProjectWizard = async () => {
    setOpeningWizard(true);
    setActionError('');
    try {
      // Clear any stale selected project before creating a new one.
      try {
        clearCurrentProject();
      } catch {
        // ignore
      }

      // Create a starter project (backend will auto-name if blank after trimming).
      const created = await api.post('/projects', {
        name: '',
        description: 'Starter project created from Mission Control. Complete Project Setup to begin.',
      });
      const p = created?.data;
      if (p?.id) {
        try {
          setCurrentProject(p);
        } catch {
          // ignore
        }
        navigate(`/projects/${p.id}/setup`, { replace: true });
        return;
      }

      // Conservative fallback
      navigate('/projects', { replace: true });
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || 'Failed to open Project Wizard';
      setActionError(String(msg));
    } finally {
      setOpeningWizard(false);
    }
  };

  const downloadHtml = async (doc: Document) => {
    try {
      const res = await api.get(
        `/projects/${finalProjectId}/documents/${doc.id}/export/html`,
        { responseType: 'blob' }
      );
      const blob = new Blob([res.data], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${typeLabel(doc.type)}_${projectName}_v${doc.version}.html`.replace(/\s+/g, '_');
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e: any) {
      alert(e?.message || 'Failed to download HTML');
    }
  };

  if (!finalProjectId) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Select or create a project to continue.</p>
          <button
            className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            onClick={() => navigate('/projects')}
          >
            Go to Projects
          </button>
        </div>
      </div>
    );
  }

  const generatedFromSetupByDocId = useMemo(() => {
    const m: Record<string, boolean> = {};
    for (const d of documents || []) {
      if (d?.id) m[d.id] = isGeneratedFromProjectSetup(d);
    }
    return m;
  }, [documents]);

  const anySetupDraftsGenerated = useMemo(() => {
    return (documents || []).some((d) => isGeneratedFromProjectSetup(d));
  }, [documents]);

  const setupDraftDocsEmpty = useMemo(() => {
    const byType: Record<string, Document> = {};
    for (const d of documents || []) {
      if (d?.type) byType[d.type] = d;
    }
    return ['rmp', 'hazard_analysis', 'fmea', 'design_inputs_doc'].every((t) => isStarterOrEmptyDoc(byType[t]));
  }, [documents]);

  const showGenerateDraftsCta = setupExists && !anySetupDraftsGenerated && setupDraftDocsEmpty;

  const runInitializeFromProfile = async () => {
    if (!finalProjectId) return;
    setGeneratingInitialDrafts(true);
    setActionError('');
    setActionInfo('');
    try {
      const res = await api.post(`/projects/${finalProjectId}/initialize-from-profile`);
      const updated = Array.isArray(res?.data?.stats?.updated_documents) ? res.data.stats.updated_documents : [];
      setActionInfo(updated.length ? `Generated drafts: ${updated.join(', ')}` : 'No drafts generated (nothing eligible).');
      await load();
    } catch (e: any) {
      const msg = e?.message || e?.response?.data?.detail || 'Failed to generate initial drafts';
      setActionError(String(msg));
    } finally {
      setGeneratingInitialDrafts(false);
    }
  };

  const runAiFmeaFromSetup = async () => {
    if (!finalProjectId) return;
    setGeneratingAiFmea(true);
    setActionError('');
    setActionInfo('');
    try {
      const out = await projectGenerateAiDraftsFromSetupApi.run(finalProjectId, ['fmea']);
      const updated = Array.isArray(out?.stats?.updated) ? out.stats.updated : [];
      const skipped = Array.isArray(out?.stats?.skipped) ? out.stats.skipped : [];
      if (updated.length) {
        setActionInfo(`AI FMEA updated: ${updated.join(', ')}`);
      } else if (skipped.length) {
        setActionInfo(`AI FMEA skipped: ${skipped.join(', ')}`);
      } else {
        setActionInfo('AI FMEA completed (no changes).');
      }
      await load();
    } catch (e: any) {
      const msg = e?.message || e?.response?.data?.detail || 'Failed to generate AI FMEA from setup';
      setActionError(String(msg));
    } finally {
      setGeneratingAiFmea(false);
    }
  };

  // Auto-run AI FMEA scoring once per project (per components count) after setup exists.
  useEffect(() => {
    if (!finalProjectId) return;
    if (!setupExists) return;
    if (state !== 'ready') return;
    if (generatingAiFmea) return;

    const key = `ai_fmea_autogen_${finalProjectId}`;
    const compsCount = String(
      (documents || []).length // fallback: keep key stable even if docs list changes
    );
    // Store a simple marker; if components change later, user can regenerate by revisiting after clearing localStorage.
    const marker = localStorage.getItem(key);
    if (marker) return;

    // Fire-and-forget with visible error banner on failure.
    // We intentionally do not show success banners by default to reduce noise.
    runAiFmeaFromSetup()
      .then(() => {
        try {
          localStorage.setItem(key, `1:${compsCount}`);
        } catch {
          // ignore
        }
      })
      .catch(() => {
        // runAiFmeaFromSetup sets actionError
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finalProjectId, setupExists, state]);

  return (
    <div className="p-6">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <div className="text-2xl font-bold text-gray-900">Mission Control</div>
          <div className="text-sm text-gray-600 mt-1">
            <span className="font-medium">Project:</span> {projectName}{' '}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            className="px-4 py-2 bg-white border border-gray-200 text-gray-900 rounded-md hover:bg-gray-50"
            onClick={load}
            disabled={state === 'loading'}
          >
            {state === 'loading' ? 'Loading…' : 'Reload'}
          </button>
          <button
            className="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700"
            onClick={() => navigate(`/projects/${finalProjectId}/documents`)}
          >
            Project Docs
          </button>
          <button
            className="px-4 py-2 bg-sky-500 text-white rounded-md hover:bg-sky-600"
            onClick={() => navigate(`/projects/${finalProjectId}/docs`)}
          >
            Documentation
          </button>
        </div>
      </div>

      {actionError ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800 font-medium">Action failed</p>
          <p className="text-red-700 text-sm mt-1">{actionError}</p>
        </div>
      ) : null}
      {/* Keep success info subtle: show only when user explicitly triggers actions like deterministic drafts. */}
      {actionInfo && !actionInfo.toLowerCase().includes('ai fmea') ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-blue-900 font-medium">Action result</p>
          <p className="text-blue-800 text-sm mt-1">{actionInfo}</p>
        </div>
      ) : null}

      {anySetupDraftsGenerated ? (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 mb-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="text-sm font-semibold text-emerald-900">Initial drafts generated from project setup</div>
              <div className="text-sm text-emerald-900/90 mt-1">
                These documents were created deterministically from your <b>Project Profile</b> and <b>Components</b>.
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {showGenerateDraftsCta ? (
        <div className="rounded-lg border border-sky-200 bg-sky-50 p-4 mb-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="text-sm font-semibold text-sky-900">Generate initial drafts</div>
              <div className="text-sm text-sky-900/90 mt-1">
                Your project setup is saved, but the key documents are still empty. Generate deterministic draft content (no AI).
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={runInitializeFromProfile}
                disabled={generatingInitialDrafts}
                className="px-4 py-2 rounded-md bg-sky-600 text-white text-sm hover:bg-sky-700 disabled:opacity-50"
              >
                {generatingInitialDrafts ? 'Generating…' : 'Generate initial drafts'}
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {setupIncomplete ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 mb-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="text-sm font-semibold text-amber-900">Complete Project Setup to unlock auto-population</div>
              <div className="text-sm text-amber-900/90 mt-1">
                Add an <b>intended use</b> and at least <b>one component</b> to enable deterministic prefill.
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => {
                  if (setupSkippedKey) localStorage.removeItem(setupSkippedKey);
                  navigate(`/projects/${finalProjectId}/setup`);
                }}
                className="px-4 py-2 rounded-md bg-amber-600 text-white text-sm hover:bg-amber-700"
              >
                Complete setup
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {state === 'error' ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800 font-medium">Failed to load project documents</p>
          <p className="text-red-700 text-sm mt-1">{error}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              onClick={load}
              type="button"
            >
              Retry
            </button>
            {String(error || '').toLowerCase().includes('project not found') ? (
              <button
                className="bg-emerald-600 text-white px-4 py-2 rounded-md hover:bg-emerald-700 disabled:opacity-50"
                onClick={openProjectWizard}
                type="button"
                disabled={openingWizard}
                title="Create a new project and open the Project Setup Wizard"
              >
                {openingWizard ? 'Opening…' : 'Project wizard'}
              </button>
            ) : null}
          </div>
        </div>
      ) : null}

      {/* Primary Next Actions (full width) */}
      <div className="mb-6">
        <NextActionsCard projectId={finalProjectId} documents={documents} />
      </div>

      {/* Key widgets */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <ProjectReadinessCard documents={documents} />
        <TraceabilityHealthCard documents={documents} />
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider">High Risk Items</div>
          <div className="mt-2 text-2xl font-bold text-gray-900">Unknown</div>
          <div className="mt-1 text-sm text-gray-600">
            We’ll surface this once risk thresholds are derived from existing risk data.
          </div>
          <div className="mt-3">
            <MiniBreakdown items={readiness.breakdown} />
          </div>
        </div>
      </div>

      {/* Hotspots + activity */}
      <div className="mt-6 grid grid-cols-1 xl:grid-cols-2 gap-4">
        <RiskHotspotsCard projectId={finalProjectId} documents={documents} />
        <RecentActivityCard projectId={finalProjectId} documents={documents} />
      </div>

      <div className="mt-6">
        {state === 'loading' ? (
          <div className="text-gray-600">Loading…</div>
        ) : (
      <DocumentHub
        projectId={finalProjectId}
        documents={documents}
        generatedFromSetupByDocId={generatedFromSetupByDocId}
      />
        )}
      </div>
    </div>
  );
}


