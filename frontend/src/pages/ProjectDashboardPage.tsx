import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import authService from '../services/authService';
import { documentsApi } from '../services/apiPhase3';
import api from '../axios';
import type { Document } from '../types';
import { docTypeById as docsRegistryById } from '../features/docs/docsRegistry';

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

const authorityBadge = (docType: string) => {
  const reg = docsRegistryById[docType];
  const authority = reg?.authority;
  if (!authority) return null;
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
};

const statusBadge = (status?: string) => {
  const s = status || 'draft';
  if (s === 'approved') return 'bg-green-100 text-green-800';
  if (s === 'in_review') return 'bg-yellow-100 text-yellow-800';
  if (s === 'obsolete') return 'bg-gray-200 text-gray-800';
  return 'bg-blue-100 text-blue-800';
};

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
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Project Dashboard</h1>
        <p className="text-gray-600 mt-1">
          <span className="font-medium">Current Project:</span> {projectName}{' '}
          <span className="text-gray-400">({finalProjectId})</span>
        </p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Project Documents</h2>
          <div className="flex gap-2">
            <button
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
              onClick={load}
              disabled={state === 'loading'}
            >
              {state === 'loading' ? 'Loading…' : 'Reload'}
            </button>
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              onClick={() => navigate(`/projects/${finalProjectId}/docs`)}
            >
              Documentation
            </button>
            <button
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              onClick={() => navigate(`/projects/${finalProjectId}/documents`)}
              title="Legacy Document Control page"
            >
              Document Control
            </button>
          </div>
        </div>

        {state === 'error' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-800 font-medium">Failed to load project documents</p>
            <p className="text-red-700 text-sm mt-1">{error}</p>
            <button
              className="mt-3 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              onClick={load}
            >
              Retry
            </button>
          </div>
        )}

        {state === 'loading' && (
          <div className="text-gray-600">Loading documents…</div>
        )}

        {state === 'ready' && documents.length === 0 && (
          <div className="text-gray-600">No documents found for this project.</div>
        )}

        {state === 'ready' && documents.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map((doc) => (
              <div key={doc.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-lg font-semibold text-gray-900">{doc.name}</div>
                    <div className="mt-1 flex flex-wrap gap-2 items-center">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {typeLabel(doc.type)}
                      </span>
                      {authorityBadge(doc.type)}
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge(doc.status)}`}>
                        {(doc.status || 'draft').toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">v{doc.version}</span>
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      Last updated: {doc.updated_at ? new Date(doc.updated_at).toLocaleString() : new Date(doc.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <button
                    className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md hover:bg-blue-700"
                    onClick={() => navigate(`/projects/${finalProjectId}/documents/${doc.id}`)}
                  >
                    Open / Edit
                  </button>
                  <button
                    className="bg-gray-200 text-gray-900 px-3 py-2 rounded-md hover:bg-gray-300"
                    onClick={() => downloadHtml(doc)}
                  >
                    Download HTML
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}


