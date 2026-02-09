import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import api from '../axios';
import authService from '../services/authService';
import { documentsApi } from '../services/apiPhase3';
import { componentsApi, projectInitializeApi, projectsApi } from '../services/apiPhase1';
import type { Document } from '../types';
import DocumentGuidanceHeader from '../components/documents/DocumentGuidanceHeader';

type Tab = 'edit' | 'preview';
type VersionScope = 'approved_only' | 'current' | 'all';

type ComponentDraft = {
  name: string;
  description?: string;
};

export default function ProjectDocumentPage() {
  const { projectId, docId } = useParams<{ projectId: string; docId: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>('');
  // Default to Preview when opening documents (users can switch to Edit when needed).
  const [tab, setTab] = useState<Tab>('preview');
  const [doc, setDoc] = useState<Document | null>(null);
  const [name, setName] = useState('');
  const [status, setStatus] = useState<Document['status']>('draft');
  const [content, setContent] = useState('');
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [didInitFmea, setDidInitFmea] = useState(false);
  const [projectName, setProjectName] = useState<string>('');

  // Add Component modal state (FMEA docs)
  const [showAddComponent, setShowAddComponent] = useState(false);
  const [componentDrafts, setComponentDrafts] = useState<ComponentDraft[]>([{ name: '', description: '' }]);
  const [addComponentBulk, setAddComponentBulk] = useState('');
  const [addComponentInfo, setAddComponentInfo] = useState<string>('');

  // Generate New modal state
  const [showGenerate, setShowGenerate] = useState(false);
  const [genComponentInput, setGenComponentInput] = useState('');
  const [genComponents, setGenComponents] = useState<string[]>([]);
  const [versionScope, setVersionScope] = useState<VersionScope>('approved_only');
  const [rmpScope, setRmpScope] = useState('');
  const [rmpIntendedUse, setRmpIntendedUse] = useState('');
  const [rmpReviewRoles, setRmpReviewRoles] = useState<Record<string, string>>({
    risk_manager: 'required',
    design_lead: 'required',
    quality_lead: 'required',
    approver: 'required',
  });
  const [genOptions, setGenOptions] = useState<Record<string, any>>({
    include_traceability: true,
    include_ai_events: false,
    include_audit_log: false,
    include_unapproved: false,
    active_controls_only: true,
    acceptability_profile: 'default_med_device',
  });

  // Versions (optional)
  const [showVersions, setShowVersions] = useState(false);
  const [versionsLoading, setVersionsLoading] = useState(false);
  const [versionsError, setVersionsError] = useState<string>('');
  const [versions, setVersions] = useState<any[]>([]);
  const [selectedVersionNo, setSelectedVersionNo] = useState<number | null>(null);

  const finalProjectId = projectId || '';
  const finalDocId = docId || '';

  const title = useMemo(() => doc?.name || 'Document', [doc]);
  const docType = (doc?.type || '').toLowerCase();
  const isRmf = docType === 'rmf';
  const isFmea = docType === 'fmea';
  const isHazardAnalysis = docType === 'hazard_analysis';
  const hasAiSample = Boolean((doc as any)?.ai_metadata?.ai_sample_generated || (doc as any)?.ai_metadata?.default_sample_provided);
  const missingSetupMessage = 'Project setup information is missing. Complete Project Setup to generate better examples.';

  function normalize(s: string | null | undefined) {
    return (s || '').trim();
  }

  const populationSources = useMemo(() => {
    // Optional, friendly chips in the header. Keep conservative and deterministic.
    const t = docType;
    const sources: string[] = [];
    if (!t) return sources;
    if (['rmp', 'hazard_analysis', 'design_inputs_doc', 'design_outputs_doc', 'vv_plan', 'vv_evidence', 'traceability_matrix', 'fmea'].includes(t)) {
      sources.push('Project Setup');
      sources.push('Components');
    }
    if (['fmea', 'risk_controls_doc', 'traceability_matrix', 'residual_risk'].includes(t)) {
      sources.push('FMEA rows');
    }
    if (['risk_controls_doc', 'residual_risk'].includes(t)) {
      sources.push('Risk Controls');
      sources.push('Risk Items');
    }
    if (t === 'rmf') {
      sources.push('Compiled from other docs');
    }
    return Array.from(new Set(sources));
  }, [docType]);

  const load = async () => {
    if (!finalProjectId || !finalDocId) return;
    setLoading(true);
    setError('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      const d = await documentsApi.getById(finalProjectId, finalDocId);
      setDoc(d);
      setName(d.name || '');
      setStatus((d.status as any) || 'draft');
      setContent(d.content || '');
    } catch (e: any) {
      setError(e?.message || 'Failed to load document');
    } finally {
      setLoading(false);
    }
  };

  const loadPreview = async () => {
    if (!finalProjectId || !finalDocId) return;
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      // FMEA preview/export is rendered from persisted FMEA rows. Ensure baseline
      // rows exist for all wizard components before exporting HTML.
      if (isFmea && !didInitFmea) {
        try {
          await projectInitializeApi.run(finalProjectId);
        } finally {
          setDidInitFmea(true);
        }
      }
      const res = await api.get(
        `/projects/${finalProjectId}/documents/${finalDocId}/export/html`,
        { responseType: 'blob', params: selectedVersionNo ? { version: selectedVersionNo } : undefined }
      );
      const blob = new Blob([res.data], { type: 'text/html' });
      const text = await blob.text();
      setPreviewHtml(text);
    } catch (e: any) {
      setPreviewHtml('');
      setError(e?.message || 'Failed to load preview');
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finalProjectId, finalDocId]);

  // Fetch project name for display (so the header matches the wizard project name).
  useEffect(() => {
    let cancelled = false;
    async function loadProjectName() {
      setProjectName('');
      if (!finalProjectId) return;
      try {
        const p = await projectsApi.getById(finalProjectId);
        if (!cancelled) setProjectName(String((p as any)?.name || ''));
      } catch {
        // non-blocking: keep showing the ID if name can't be loaded
      }
    }
    loadProjectName();
    return () => {
      cancelled = true;
    };
  }, [finalProjectId]);

  // When navigating between documents, reset the UI to Preview by default.
  useEffect(() => {
    setTab('preview');
    setPreviewHtml('');
    setDidInitFmea(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finalProjectId, finalDocId]);

  useEffect(() => {
    if (tab === 'preview' && finalProjectId && finalDocId) {
      loadPreview();
    }
  }, [tab, selectedVersionNo, finalProjectId, finalDocId]);

  const save = async () => {
    if (!finalProjectId || !finalDocId) return;
    if (isRmf) {
      setError("RMF is compiled and cannot be edited manually. Use 'Compile Risk Management File'.");
      return;
    }
    setSaving(true);
    setError('');
    try {
      const updated = await documentsApi.update(finalProjectId, finalDocId, {
        name,
        status,
        content,
      } as any);
      setDoc(updated);
      if (tab === 'preview') {
        await loadPreview();
      }
    } catch (e: any) {
      setError(e?.message || 'Failed to save document');
    } finally {
      setSaving(false);
    }
  };

  const downloadHtml = async () => {
    try {
      const res = await api.get(
        `/projects/${finalProjectId}/documents/${finalDocId}/export/html`,
        { responseType: 'blob', params: selectedVersionNo ? { version: selectedVersionNo } : undefined }
      );
      const blob = new Blob([res.data], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const v = selectedVersionNo || doc?.version || 1;
      a.download = `${title}_v${v}.html`.replace(/\s+/g, '_');
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e?.message || 'Failed to download HTML');
    }
  };

  const downloadCsv = async () => {
    try {
      const res = await api.get(`/projects/${finalProjectId}/documents/${finalDocId}/export/csv`, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const v = selectedVersionNo || doc?.version || 1;
      a.download = `${title}_v${v}.csv`.replace(/\s+/g, '_');
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e?.message || 'Failed to download CSV');
    }
  };

  const addGenComponentsFromInput = () => {
    const parts = genComponentInput
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean);
    if (parts.length === 0) return;
    setGenComponents((prev) => Array.from(new Set([...prev, ...parts])));
    setGenComponentInput('');
  };

  const generateNew = async () => {
    if (!finalProjectId || !finalDocId) return;
    setSaving(true);
    setError('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      if (isFmea) {
        await projectInitializeApi.run(finalProjectId);
        setDidInitFmea(true);
      }
      const payload = {
        components: genComponents.map((name) => ({ name })),
        version_scope: versionScope,
        options:
          docType === 'rmp'
            ? {
                ...genOptions,
                scope: rmpScope,
                intended_use: rmpIntendedUse,
                review_roles: rmpReviewRoles,
              }
            : genOptions,
      };
      const res = await api.post(
        `/projects/${finalProjectId}/documents/${finalDocId}/generate`,
        payload
      );
      const newVersionNo = res.data?.new_version_no;
      const html = res.data?.rendered_html || '';
      setSelectedVersionNo(null);
      setPreviewHtml(html);
      setTab('preview');
      setShowGenerate(false);
      await load(); // refresh doc metadata/version
      alert(`Generated version v${newVersionNo}`);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to generate new version');
    } finally {
      setSaving(false);
    }
  };

  const addComponentRow = () => {
    setComponentDrafts((prev) => [...prev, { name: '', description: '' }]);
  };

  const removeComponentRow = (idx: number) => {
    setComponentDrafts((prev) => {
      const next = prev.filter((_, i) => i !== idx);
      return next.length ? next : [{ name: '', description: '' }];
    });
  };

  const applyAddComponentBulk = () => {
    const lines = addComponentBulk
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean);
    if (!lines.length) return;
    setComponentDrafts((prev) => {
      const existing = new Set(prev.map((c) => normalize(c.name).toLowerCase()).filter(Boolean));
      const additions: ComponentDraft[] = [];
      for (const name of lines) {
        const key = name.toLowerCase();
        if (existing.has(key)) continue;
        existing.add(key);
        additions.push({ name, description: '' });
      }
      const cleanedPrev = prev.filter((c) => normalize(c.name) || normalize(c.description));
      const base = cleanedPrev.length ? cleanedPrev : [];
      return [...base, ...additions, ...(base.length || additions.length ? [] : [{ name: '', description: '' }])];
    });
    setAddComponentBulk('');
  };

  const addComponentsToProject = async () => {
    if (!finalProjectId) return;
    setSaving(true);
    setError('');
    setAddComponentInfo('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }

      const toCreate = componentDrafts
        .map((c) => ({ name: normalize(c.name), description: normalize(c.description) }))
        .filter((c) => c.name);

      if (toCreate.length === 0) {
        setError('Please enter at least one component name.');
        return;
      }

      // Create components
      for (const c of toCreate) {
        await componentsApi.create(finalProjectId, { name: c.name, description: c.description || undefined });
      }

      // Seed baseline FMEA rows (>= 5 rows per component)
      await projectInitializeApi.run(finalProjectId);

      // For FMEA docs, regenerate so the preview table reflects the newly seeded rows.
      if (isFmea && finalDocId) {
        const payload = {
          components: [],
          version_scope: versionScope,
          options: genOptions,
        };
        const res = await api.post(`/projects/${finalProjectId}/documents/${finalDocId}/generate`, payload);
        const html = res.data?.rendered_html || '';
        setSelectedVersionNo(null);
        setPreviewHtml(html);
        setTab('preview');
        await load(); // refresh doc metadata/version
      }

      setAddComponentInfo(`Added ${toCreate.length} component${toCreate.length === 1 ? '' : 's'} and seeded FMEA rows.`);
      setShowAddComponent(false);
      setComponentDrafts([{ name: '', description: '' }]);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to add component(s)');
    } finally {
      setSaving(false);
    }
  };

  const generateAiSample = async () => {
    if (!finalProjectId || !docType) return;
    if (!doc) return;
    setSaving(true);
    setError('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      if (isFmea) {
        await projectInitializeApi.run(finalProjectId);
        setDidInitFmea(true);
      }
      const updated = await documentsApi.generateAiSampleForType(finalProjectId, docType);
      setDoc(updated);
      setName(updated.name || '');
      setStatus((updated.status as any) || 'draft');
      setContent(updated.content || '');
      setSelectedVersionNo(null);
      setTab('preview');
      await loadPreview();
      alert('AI sample added as a new draft version.');
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to generate AI sample');
    } finally {
      setSaving(false);
    }
  };

  const generateWithAi = async () => {
    if (!finalProjectId || !docType) return;
    if (!doc) return;
    setSaving(true);
    setError('');
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      if (isFmea) {
        await projectInitializeApi.run(finalProjectId);
        setDidInitFmea(true);
      }
      if (isHazardAnalysis && finalDocId) {
        // Hazard Analysis: "Generate with AI" enriches risk chain fields, then regenerates the deterministic table.
        const enrichRes = await api.post(`/projects/${finalProjectId}/hazard-analysis/enrich-ai`, {
          max_items: 50,
          only_if_missing: true,
        });
        const stats = enrichRes?.data?.stats;

        // Ensure the regenerated table actually shows the versions we just created.
        // (Newly enriched versions are not "approved", so approved_only would look like "nothing happened".)
        const nextVersionScope = versionScope === 'approved_only' ? 'current' : versionScope;
        const payload = {
          components: [],
          version_scope: nextVersionScope,
          options: { ...genOptions, include_unapproved: true },
        };
        const res = await api.post(`/projects/${finalProjectId}/documents/${finalDocId}/generate`, payload);
        const html = res.data?.rendered_html || '';
        setSelectedVersionNo(null);
        setPreviewHtml(html);
        setTab('preview');
        await load(); // refresh doc metadata/version
        if (stats && typeof stats.updated === 'number') {
          alert(
            `Hazard Analysis enrichment complete: updated ${stats.updated} item(s) (scanned ${stats.scanned || 0}). Regenerated table.`
          );
        } else {
          alert('Filled missing hazard chain fields and regenerated Hazard Analysis.');
        }
      } else {
        const updated = await documentsApi.generateWithAiForType(finalProjectId, docType);
        setDoc(updated);
        setName(updated.name || '');
        setStatus((updated.status as any) || 'draft');
        setContent(updated.content || '');
        setSelectedVersionNo(null);
        setTab('preview');
        await loadPreview();
        alert('AI populated draft created as a new version.');
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to generate with AI');
    } finally {
      setSaving(false);
    }
  };

  const openVersions = async () => {
    if (!finalProjectId || !finalDocId) return;
    setShowVersions(true);
    setVersionsError('');
    setVersionsLoading(true);
    try {
      const list = await documentsApi.getVersions(finalProjectId, finalDocId);
      setVersions(Array.isArray(list) ? list : []);
    } catch (e: any) {
      setVersionsError(e?.message || 'Failed to load versions');
    } finally {
      setVersionsLoading(false);
    }
  };

  const viewVersion = (v: any) => {
    setSelectedVersionNo(v.version);
    setTab('preview');
    // Prefer content if it looks like full HTML
    if (typeof v.content === 'string' && v.content.trim().startsWith('<')) {
      setPreviewHtml(v.content);
    } else {
      setPreviewHtml('');
    }
    setShowVersions(false);
  };

  if (!finalProjectId || !finalDocId) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Project and document id are required.</p>
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

  if (loading) {
    return <div className="p-6 text-gray-600">Loading document…</div>;
  }

  return (
    <div className="p-6">
      <DocumentGuidanceHeader
        documentType={docType || 'document'}
        hasAiSample={hasAiSample}
        onGenerateAiSample={generateAiSample}
        onGenerateWithAi={generateWithAi}
        isGeneratingAi={saving}
        populationSources={populationSources}
      />
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
            <p className="text-gray-500 text-sm mt-1">
              Project:{' '}
              <span className="font-semibold text-gray-700">{projectName || '—'}</span>
            </p>
          </div>
          <div className="flex gap-2">
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              onClick={() => setShowGenerate(true)}
              disabled={saving}
            >
              {isRmf ? 'Compile RMF' : 'Generate New'}
            </button>
            <button
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:bg-gray-400"
              onClick={save}
              disabled={saving || isRmf}
              title="Save Draft"
            >
              {saving ? 'Saving…' : 'Save Draft'}
            </button>
            <button
              className="bg-gray-200 text-gray-900 px-4 py-2 rounded-md hover:bg-gray-300"
              onClick={() => navigate(`/projects/${finalProjectId}/dashboard`)}
            >
              Back
            </button>
            <button
              className="bg-gray-200 text-gray-900 px-4 py-2 rounded-md hover:bg-gray-300"
              onClick={openVersions}
            >
              View Versions
            </button>
            <button
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              onClick={isFmea ? downloadCsv : downloadHtml}
            >
              {isFmea ? 'Download CSV' : 'Download HTML'}
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
            {String(error).includes(missingSetupMessage) ? (
              <div className="mt-2">
                <Link
                  to={`/projects/${finalProjectId}/setup`}
                  className="text-sm font-medium text-blue-700 underline"
                >
                  Complete Project Setup
                </Link>
              </div>
            ) : null}
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex gap-2">
            <button
              className={`px-4 py-2 rounded-md ${tab === 'edit' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-900 hover:bg-gray-300'}`}
              onClick={() => setTab('edit')}
              disabled={isRmf}
            >
              Edit
            </button>
            <button
              className={`px-4 py-2 rounded-md ${tab === 'preview' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-900 hover:bg-gray-300'}`}
              onClick={() => setTab('preview')}
            >
              Preview
            </button>
            {isFmea ? (
              <button
                className="px-4 py-2 rounded-md bg-gray-200 text-gray-900 hover:bg-gray-300"
                onClick={() => {
                  setAddComponentInfo('');
                  setShowAddComponent(true);
                }}
                type="button"
              >
                Add Component
              </button>
            ) : null}
          </div>
          <div className="text-sm text-gray-500">
            {selectedVersionNo ? `Viewing version v${selectedVersionNo}` : `Current version v${doc?.version || 1}`}
          </div>
        </div>

        {addComponentInfo ? (
          <div className="mb-4 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800">
            {addComponentInfo}
          </div>
        ) : null}

        {tab === 'edit' && !isRmf ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={status}
                  onChange={(e) => setStatus(e.target.value as any)}
                >
                  <option value="draft">Draft</option>
                  <option value="in_review">In Review</option>
                  <option value="approved">Approved</option>
                  <option value="obsolete">Obsolete</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
                rows={18}
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-auto">
            {previewHtml ? (
              <div dangerouslySetInnerHTML={{ __html: previewHtml }} />
            ) : (
              <div className="text-gray-600">No preview available.</div>
            )}
          </div>
        )}
      </div>

      {/* Add Component Modal (FMEA) */}
      {showAddComponent && isFmea && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-3xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Add Component(s) to Project</h3>
              <button
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                onClick={() => setShowAddComponent(false)}
                type="button"
              >
                Close
              </button>
            </div>

            <div className="text-sm text-gray-700 mb-4">
              This will add component(s) to your project and seed <b>at least 5 FMEA rows per component</b>.
              {isFmea ? ' The FMEA document preview will be regenerated to include the new rows.' : null}
            </div>

            <div className="space-y-4">
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <div className="text-sm font-semibold text-gray-900 mb-2">Bulk add</div>
                <div className="text-sm text-gray-600 mb-2">Paste one component name per line.</div>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  rows={4}
                  value={addComponentBulk}
                  onChange={(e) => setAddComponentBulk(e.target.value)}
                  placeholder="e.g.\nBattery pack\nCharging port\nSensor assembly"
                />
                <div className="mt-2 flex justify-end">
                  <button
                    type="button"
                    onClick={applyAddComponentBulk}
                    className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
                    disabled={!addComponentBulk.trim()}
                  >
                    Add lines
                  </button>
                </div>
              </div>

              <div className="rounded-lg border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-sm font-semibold text-gray-900">Components to add</div>
                  <button
                    type="button"
                    onClick={addComponentRow}
                    className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
                  >
                    + Add row
                  </button>
                </div>

                <div className="space-y-3">
                  {componentDrafts.map((c, idx) => (
                    <div key={idx} className="grid grid-cols-1 md:grid-cols-12 gap-2 items-start">
                      <div className="md:col-span-4">
                        <label className="block text-xs font-medium text-gray-600 mb-1">Name</label>
                        <input
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          value={c.name}
                          onChange={(e) => {
                            const v = e.target.value;
                            setComponentDrafts((prev) => prev.map((x, i) => (i === idx ? { ...x, name: v } : x)));
                          }}
                          placeholder="Component name"
                        />
                      </div>
                      <div className="md:col-span-7">
                        <label className="block text-xs font-medium text-gray-600 mb-1">Description (optional)</label>
                        <input
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          value={c.description || ''}
                          onChange={(e) => {
                            const v = e.target.value;
                            setComponentDrafts((prev) =>
                              prev.map((x, i) => (i === idx ? { ...x, description: v } : x))
                            );
                          }}
                          placeholder="Short description"
                        />
                      </div>
                      <div className="md:col-span-1 flex md:justify-end pt-6">
                        <button
                          type="button"
                          className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
                          onClick={() => removeComponentRow(idx)}
                          title="Remove"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-end gap-2">
                <button
                  type="button"
                  className="px-4 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
                  onClick={() => setShowAddComponent(false)}
                  disabled={saving}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="px-4 py-2 rounded-md text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                  onClick={addComponentsToProject}
                  disabled={saving}
                >
                  {saving ? 'Adding…' : 'Add component(s)'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Generate New Modal */}
      {showGenerate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Generate New Version</h3>
              <button
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                onClick={() => setShowGenerate(false)}
              >
                Close
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Components</label>
                <div className="flex gap-2">
                  <input
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Add components (comma-separated)…"
                    value={genComponentInput}
                    onChange={(e) => setGenComponentInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        addGenComponentsFromInput();
                      }
                    }}
                  />
                  <button
                    className="bg-gray-200 px-4 py-2 rounded-md hover:bg-gray-300"
                    onClick={addGenComponentsFromInput}
                  >
                    Add
                  </button>
                </div>
                {genComponents.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {genComponents.map((c) => (
                      <span key={c} className="inline-flex items-center gap-2 px-2 py-1 bg-gray-100 rounded-full text-sm">
                        {c}
                        <button
                          className="text-gray-500 hover:text-gray-800"
                          onClick={() => setGenComponents((prev) => prev.filter((x) => x !== c))}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {(docType === 'hazard_analysis' || docType === 'residual_risk') && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Version scope</label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      value={versionScope}
                      onChange={(e) => setVersionScope(e.target.value as any)}
                    >
                      <option value="approved_only">Approved only</option>
                      <option value="current">Current</option>
                      <option value="all">All</option>
                    </select>
                  </div>
                  <label className="flex items-center gap-2 text-sm text-gray-700 mt-6">
                    <input
                      type="checkbox"
                      checked={!!genOptions.include_unapproved}
                      onChange={(e) => setGenOptions((o) => ({ ...o, include_unapproved: e.target.checked }))}
                    />
                    Include unapproved
                  </label>
                </div>
              )}

              {docType === 'rmf' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.include_traceability}
                      onChange={(e) => setGenOptions((o) => ({ ...o, include_traceability: e.target.checked }))}
                    />
                    Include traceability
                  </label>
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.include_ai_events}
                      onChange={(e) => setGenOptions((o) => ({ ...o, include_ai_events: e.target.checked }))}
                    />
                    Include AI events
                  </label>
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.include_audit_log}
                      onChange={(e) => setGenOptions((o) => ({ ...o, include_audit_log: e.target.checked }))}
                    />
                    Include audit log
                  </label>
                </div>
              )}

              {docType === 'risk_controls_doc' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.active_controls_only}
                      onChange={(e) => setGenOptions((o) => ({ ...o, active_controls_only: e.target.checked }))}
                    />
                    Active controls only
                  </label>
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={!!genOptions.include_traceability}
                      onChange={(e) => setGenOptions((o) => ({ ...o, include_traceability: e.target.checked }))}
                    />
                    Include traceability details
                  </label>
                </div>
              )}

              {docType === 'residual_risk' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Acceptability profile</label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      value={genOptions.acceptability_profile}
                      onChange={(e) => setGenOptions((o) => ({ ...o, acceptability_profile: e.target.value }))}
                    >
                      <option value="default_med_device">Default medical device</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>
                </div>
              )}

              {docType === 'rmp' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Scope</label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      rows={3}
                      placeholder="Define the scope of the Risk Management Plan…"
                      value={rmpScope}
                      onChange={(e) => setRmpScope(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Intended Use</label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      rows={3}
                      placeholder="Describe intended use, users, environment, and lifecycle…"
                      value={rmpIntendedUse}
                      onChange={(e) => setRmpIntendedUse(e.target.value)}
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Acceptability profile</label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        value={genOptions.acceptability_profile}
                        onChange={(e) => setGenOptions((o) => ({ ...o, acceptability_profile: e.target.value }))}
                      >
                        <option value="default_med_device">Default medical device</option>
                        <option value="custom">Custom</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <div className="block text-sm font-medium text-gray-700 mb-2">Review roles</div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(rmpReviewRoles).map(([role, requirement]) => (
                        <label key={role} className="text-sm text-gray-700">
                          <div className="mb-1 font-medium">{role.replace(/_/g, ' ')}</div>
                          <select
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                            value={requirement}
                            onChange={(e) =>
                              setRmpReviewRoles((prev) => ({ ...prev, [role]: e.target.value }))
                            }
                          >
                            <option value="required">required</option>
                            <option value="optional">optional</option>
                          </select>
                        </label>
                      ))}
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      Tip: leave Scope/Intended Use blank to generate with placeholders and edit later.
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  className="bg-gray-200 px-4 py-2 rounded-md hover:bg-gray-300"
                  onClick={() => setShowGenerate(false)}
                  disabled={saving}
                >
                  Cancel
                </button>
                <button
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                  onClick={generateNew}
                  disabled={saving}
                >
                  {saving ? 'Generating…' : 'Generate'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Versions Modal */}
      {showVersions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Document Versions</h3>
              <button
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                onClick={() => setShowVersions(false)}
              >
                Close
              </button>
            </div>
            {versionsLoading ? (
              <div className="text-gray-600">Loading…</div>
            ) : versionsError ? (
              <div className="text-red-700">{versionsError}</div>
            ) : versions.length === 0 ? (
              <div className="text-gray-600">No versions found.</div>
            ) : (
              <div className="space-y-2">
                {versions.map((v) => (
                  <div key={v.id} className="border border-gray-200 rounded-md p-3 flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">v{v.version}</div>
                      <div className="text-xs text-gray-500">{new Date(v.created_at).toLocaleString()}</div>
                      {v?.changes?.generated && (
                        <div className="text-xs text-blue-600 mt-1">Generated</div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <button
                        className="bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700"
                        onClick={() => viewVersion(v)}
                      >
                        View
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}


