import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Button } from '../../components/ui/Button';
import { projectProfileApi } from '../../services/apiPhase1';
import {
  generatePmsPlan,
  listPmsPlans,
  openPmsPlanPrintView,
  PmsPlanHistoryItem,
} from '../../api/pmsPlan';

const PmsPlanGeneratorPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const finalProjectId = projectId || currentProject?.id || '';

  const [items, setItems] = useState<PmsPlanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deviceName, setDeviceName] = useState('');
  const [intendedUse, setIntendedUse] = useState('');

  const loadList = useCallback(async () => {
    if (!finalProjectId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await listPmsPlans(finalProjectId);
      setItems(res.items || []);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load PMS plans');
    } finally {
      setLoading(false);
    }
  }, [finalProjectId]);

  useEffect(() => {
    loadList();
  }, [loadList]);

  useEffect(() => {
    if (!finalProjectId) return;
    let cancelled = false;
    (async () => {
      try {
        const profile = await projectProfileApi.get(finalProjectId);
        if (cancelled) return;
        const name = currentProject?.name || '';
        if (!deviceName && name) setDeviceName(name);
        if (!intendedUse && profile?.intended_use) setIntendedUse(String(profile.intended_use));
        if (!deviceName && profile?.device_description) {
          setDeviceName((prev) => prev || String(profile.device_description).slice(0, 200));
        }
      } catch {
        /* profile optional */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [finalProjectId, currentProject?.name]);

  const handleGenerate = async () => {
    if (!finalProjectId) return;
    const dn = deviceName.trim();
    const iu = intendedUse.trim();
    if (!dn || !iu) {
      setError('Device name and intended use are required.');
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      const res = await generatePmsPlan({
        project_id: finalProjectId,
        device_name: dn,
        intended_use: iu,
      });
      await loadList();
      navigate(`/projects/${finalProjectId}/pms/plan-generator/${res.generation_id}`);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const formatDate = (iso: string) => {
    try {
      return new Date(iso).toLocaleString();
    } catch {
      return iso;
    }
  };

  if (!finalProjectId) {
    return (
      <div className="p-6 text-neutral-600">
        Select a project from the sidebar, or open this page from a project dashboard.
        <div className="mt-4">
          <Link to="/projects" className="text-blue-600 underline">
            Go to projects
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 px-4 py-6 sm:px-6 lg:px-8">
      <PageHeader
        title="PMS plan generator"
        breadcrumbs={[
          { label: 'Projects', path: '/projects' },
          { label: 'Dashboard', path: `/projects/${finalProjectId}/dashboard` },
          { label: 'PMS plan' },
        ]}
        subtitle="Build ISO 14971–aligned post-market surveillance plans from FMEA + simulated MAUDE-like signals (AI-assisted)."
      />

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
      )}

      <div className="mb-8 rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-neutral-900">Generate new plan</h2>
        <p className="mt-1 text-sm text-neutral-600">
          Uses project FMEA rows and deterministic simulated adverse-event themes. Output is saved and appears in the
          table below.
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-neutral-700">Device name</label>
            <input
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm"
              value={deviceName}
              onChange={(e) => setDeviceName(e.target.value)}
              placeholder="e.g. Implantable pulse generator Model X"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-neutral-700">Intended use</label>
            <textarea
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm"
              rows={3}
              value={intendedUse}
              onChange={(e) => setIntendedUse(e.target.value)}
              placeholder="From risk management / labeling — concise statement"
            />
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button onClick={handleGenerate} disabled={generating}>
            {generating ? 'Generating…' : 'Generate PMS plan'}
          </Button>
        </div>
      </div>

      <div className="rounded-xl border border-neutral-200 bg-white shadow-sm overflow-hidden">
        <div className="border-b border-neutral-200 bg-neutral-50 px-4 py-3">
          <h2 className="text-lg font-semibold text-neutral-900">Saved plans</h2>
          <p className="text-xs text-neutral-500">Newest first. Includes legacy runs stored only in audit log.</p>
        </div>
        {loading ? (
          <div className="p-8 text-center text-neutral-500">Loading…</div>
        ) : items.length === 0 ? (
          <div className="p-8 text-center text-neutral-500">No plans yet. Generate one above.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-neutral-200 bg-neutral-50 text-xs uppercase text-neutral-500">
                <tr>
                  <th className="px-4 py-3">Created</th>
                  <th className="px-4 py-3">Device</th>
                  <th className="px-4 py-3">Summary</th>
                  <th className="px-4 py-3">v / FMEA</th>
                  <th className="px-4 py-3">Model</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {items.map((row) => (
                  <tr key={row.id} className="hover:bg-neutral-50">
                    <td className="whitespace-nowrap px-4 py-3 text-neutral-700">{formatDate(row.created_at)}</td>
                    <td className="max-w-[140px] truncate px-4 py-3 text-neutral-800" title={row.device_name || ''}>
                      {row.device_name || '—'}
                    </td>
                    <td className="max-w-md truncate px-4 py-3 text-neutral-600" title={row.summary || ''}>
                      {row.summary || '—'}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-neutral-600">
                      v{row.version ?? '—'} · {row.fmea_row_count ?? '—'} rows
                    </td>
                    <td className="max-w-[100px] truncate px-4 py-3 text-neutral-500" title={row.model || ''}>
                      {row.model || '—'}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-right">
                      <Link
                        to={`/projects/${finalProjectId}/pms/plan-generator/${row.id}`}
                        className="mr-2 text-blue-600 hover:underline"
                      >
                        View
                      </Link>
                      <button
                        type="button"
                        className="text-neutral-600 hover:text-neutral-900 hover:underline"
                        onClick={() => openPmsPlanPrintView(row.id).catch((err) => setError(String(err.message)))}
                      >
                        Print / PDF
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default PmsPlanGeneratorPage;
