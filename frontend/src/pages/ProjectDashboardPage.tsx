import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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

type LoadState = 'idle' | 'loading' | 'error' | 'ready';

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
  const { currentProject, setCurrentProject } = useProject();

  const [state, setState] = useState<LoadState>('idle');
  const [error, setError] = useState<string>('');
  const [documents, setDocuments] = useState<Document[]>([]);

  const finalProjectId = projectId || '';

  const projectName = useMemo(() => {
    if (currentProject?.id === finalProjectId) return currentProject.name;
    return 'Project';
  }, [currentProject, finalProjectId]);

  const readiness = useMemo(() => computeReadiness(documents), [documents]);

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
    } catch (e: any) {
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
  }, [finalProjectId]);

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

  return (
    <div className="p-6">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <div className="text-2xl font-bold text-gray-900">Mission Control</div>
          <div className="text-sm text-gray-600 mt-1">
            <span className="font-medium">Project:</span> {projectName}{' '}
            <span className="text-gray-400">({finalProjectId})</span>
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

      {state === 'error' ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800 font-medium">Failed to load project documents</p>
          <p className="text-red-700 text-sm mt-1">{error}</p>
          <button
            className="mt-3 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
            onClick={load}
          >
            Retry
          </button>
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
          <DocumentHub projectId={finalProjectId} documents={documents} />
        )}
      </div>
    </div>
  );
}


