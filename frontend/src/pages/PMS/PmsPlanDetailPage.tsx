import React, { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Button } from '../../components/ui/Button';
import { getPmsPlan, openPmsPlanPrintView, PmsPlanHistoryItem } from '../../api/pmsPlan';

const SECTION_ORDER: { key: keyof PmsPlanHistoryItem['plan']; label: string }[] = [
  { key: 'device_overview', label: 'Device overview' },
  { key: 'pms_objectives', label: 'PMS objectives' },
  { key: 'data_sources', label: 'Data sources' },
  { key: 'maude_analysis', label: 'MAUDE analysis' },
  { key: 'risk_mapping', label: 'Risk mapping' },
  { key: 'signal_detection', label: 'Signal detection' },
  { key: 'pms_activities', label: 'PMS activities' },
  { key: 'capa_integration', label: 'CAPA integration' },
  { key: 'benefit_risk', label: 'Benefit–risk' },
  { key: 'reporting', label: 'Reporting' },
];

const PmsPlanDetailPage: React.FC = () => {
  const { projectId, generationId } = useParams<{ projectId: string; generationId: string }>();
  const { currentProject } = useProject();
  const finalProjectId = projectId || currentProject?.id || '';

  const [item, setItem] = useState<PmsPlanHistoryItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [printBusy, setPrintBusy] = useState(false);

  const load = useCallback(async () => {
    if (!generationId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getPmsPlan(generationId);
      if (finalProjectId && data.project_id !== finalProjectId) {
        setError('This plan belongs to a different project.');
        setItem(null);
        return;
      }
      setItem(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load plan');
      setItem(null);
    } finally {
      setLoading(false);
    }
  }, [generationId, finalProjectId]);

  useEffect(() => {
    load();
  }, [load]);

  const handlePrint = async () => {
    if (!generationId) return;
    setPrintBusy(true);
    try {
      await openPmsPlanPrintView(generationId);
    } catch (e: any) {
      setError(e?.message || 'Could not open print view');
    } finally {
      setPrintBusy(false);
    }
  };

  if (!generationId) {
    return <div className="p-6 text-neutral-600">Missing plan id.</div>;
  }

  if (loading) {
    return <div className="p-6 text-neutral-600">Loading plan…</div>;
  }

  if (error && !item) {
    return (
      <div className="p-6">
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-800">{error}</div>
        {finalProjectId ? (
          <Link to={`/projects/${finalProjectId}/pms/plan-generator`} className="mt-4 inline-block text-blue-600 underline">
            Back to PMS plans
          </Link>
        ) : null}
      </div>
    );
  }

  if (!item) return null;

  return (
    <div className="min-h-screen bg-neutral-50 px-4 py-6 sm:px-6 lg:px-8">
      <PageHeader
        title="PMS plan"
        breadcrumbs={[
          { label: 'Projects', path: '/projects' },
          ...(finalProjectId
            ? ([
                { label: 'Dashboard', path: `/projects/${finalProjectId}/dashboard` },
                { label: 'PMS plans', path: `/projects/${finalProjectId}/pms/plan-generator` },
              ] as const)
            : []),
          { label: item.summary?.slice(0, 40) || item.id.slice(0, 8) },
        ]}
        subtitle={`${item.device_name || 'Device'} · v${item.version ?? '?'} · ${new Date(item.created_at).toLocaleString()}`}
        actions={
          <div className="flex flex-wrap gap-2">
            {finalProjectId ? (
              <Link to={`/projects/${finalProjectId}/pms/plan-generator`}>
                <Button variant="secondary">All plans</Button>
              </Link>
            ) : null}
            <Button variant="secondary" onClick={handlePrint} disabled={printBusy}>
              {printBusy ? 'Opening…' : 'Print / Save as PDF'}
            </Button>
          </div>
        }
      />

      {item.warning ? (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <strong>Limited scope:</strong> {item.warning}
        </div>
      ) : null}

      {error ? (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
      ) : null}

      <div className="mb-6 rounded-xl border border-neutral-200 bg-white p-4 shadow-sm">
        <h2 className="text-sm font-semibold text-neutral-800">Metadata</h2>
        <dl className="mt-2 grid gap-2 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-neutral-500">Generation ID</dt>
            <dd className="font-mono text-xs text-neutral-800">{item.id}</dd>
          </div>
          <div>
            <dt className="text-neutral-500">FMEA rows referenced</dt>
            <dd className="text-neutral-800">{item.fmea_row_count ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-neutral-500">AI model</dt>
            <dd className="text-neutral-800">{item.model || '—'}</dd>
          </div>
          <div>
            <dt className="text-neutral-500">AI-generated</dt>
            <dd className="text-neutral-800">{item.ai_generated === true ? 'Yes' : item.ai_generated === false ? 'No' : '—'}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-neutral-500">Summary</dt>
            <dd className="text-neutral-800">{item.summary || '—'}</dd>
          </div>
        </dl>
      </div>

      <div className="mb-6 rounded-xl border border-neutral-200 bg-white shadow-sm overflow-hidden">
        <div className="border-b border-neutral-200 bg-neutral-50 px-4 py-3">
          <h2 className="text-lg font-semibold text-neutral-900">Simulated MAUDE-like signals</h2>
          <p className="text-xs text-neutral-500">For planning only — not verified FDA MAUDE extracts.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-neutral-200 bg-neutral-50 text-xs uppercase text-neutral-500">
              <tr>
                <th className="px-4 py-2">Failure theme</th>
                <th className="px-4 py-2">Count</th>
                <th className="px-4 py-2">Trend</th>
                <th className="px-4 py-2">Severity</th>
                <th className="px-4 py-2">Monitoring focus</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {(item.maude_signals || []).length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-4 text-neutral-500">
                    No signals
                  </td>
                </tr>
              ) : (
                item.maude_signals.map((s, i) => (
                  <tr key={i}>
                    <td className="px-4 py-2 text-neutral-800">{s.failure_mode}</td>
                    <td className="px-4 py-2">{s.event_count}</td>
                    <td className="px-4 py-2">{s.trend}</td>
                    <td className="px-4 py-2">{s.severity}</td>
                    <td className="max-w-md px-4 py-2 text-neutral-600">{s.recommended_monitoring_focus || '—'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="space-y-4">
        {SECTION_ORDER.map(({ key, label }) => (
          <section key={key} className="rounded-xl border border-neutral-200 bg-white shadow-sm">
            <details open className="group">
              <summary className="cursor-pointer list-none border-b border-neutral-100 px-4 py-3 font-semibold text-neutral-900">
                {label}
              </summary>
              <div className="whitespace-pre-wrap px-4 py-4 text-sm leading-relaxed text-neutral-800">
                {item.plan[key] || '—'}
              </div>
            </details>
          </section>
        ))}
      </div>
    </div>
  );
};

export default PmsPlanDetailPage;
