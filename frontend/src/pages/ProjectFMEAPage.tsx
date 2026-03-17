import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../axios';
import { componentsApi, fmeaApi, projectInitializeApi, projectsApi } from '../services/apiPhase1';
import { generateVVFromRisk } from '../services/vvFromRiskApi';
import { FmeaRow } from '../types';
import FmeaTable from '../components/FMEA/FmeaTable';
import { GenerateVVModal } from '../components/VV/GenerateVVModal';

type GeneratedRow = {
  id: string;
  component: string;
  function: string;
  failureMode: string;
  potentialEffect: string;
  severity: number;
  potentialCauses: string;
  occurrence: number;
  currentControls: string;
  detection: number;
  rpn: number;
  recommendedActions: string;
  responsible: string;
  targetDate: string;
  actionsTaken: string;
  finalSeverity: number;
  finalOccurrence: number;
  finalDetection: number;
  finalRpn: number;
};

function getRpnClass(rpn: number) {
  // Align with `FMEAPage.tsx` (low < 50, medium 50–99, high >= 100)
  if (rpn >= 100) return 'bg-red-100 text-red-800';
  if (rpn >= 50) return 'bg-yellow-100 text-yellow-800';
  return 'bg-green-100 text-green-800';
}

function clampScore(n: any): number {
  const v = Number(n);
  if (!Number.isFinite(v)) return 1;
  return Math.max(1, Math.min(10, Math.round(v)));
}

async function mapWithConcurrency<T, R>(
  items: T[],
  limit: number,
  fn: (item: T, index: number) => Promise<R>
): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let nextIndex = 0;

  async function worker() {
    while (true) {
      const idx = nextIndex++;
      if (idx >= items.length) return;
      results[idx] = await fn(items[idx], idx);
    }
  }

  const workers = Array.from({ length: Math.max(1, limit) }, () => worker());
  await Promise.all(workers);
  return results;
}

export default function ProjectFMEAPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [fmeaType, setFmeaType] = useState<'design' | 'process'>('design');
  const [componentDescription, setComponentDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string>('');
  const [info, setInfo] = useState<string>('');
  const [rows, setRows] = useState<GeneratedRow[]>([]);

  // Persisted rows (includes wizard-seeded starter rows)
  const [savedRows, setSavedRows] = useState<FmeaRow[]>([]);
  const [loadingSaved, setLoadingSaved] = useState(false);
  const [savedError, setSavedError] = useState<string>('');
  const [componentNameById, setComponentNameById] = useState<Record<string, string>>({});
  // Default view should be table (users can still toggle to grid per-session).
  const [savedView, setSavedView] = useState<'grid' | 'table'>('table');
  const [didAutoSeed, setDidAutoSeed] = useState(false);

  // Generate V&V from risk modal
  const [vvModalOpen, setVVModalOpen] = useState(false);
  const [vvLoading, setVVLoading] = useState(false);
  const [vvError, setVVError] = useState<string | null>(null);
  const [vvData, setVVData] = useState<any>(null);
  const [vvRow, setVVRow] = useState<FmeaRow | null>(null);

  const canSave = rows.length > 0 && !isGenerating && !isSaving && !!projectId;

  const sortedSavedRows = useMemo(() => {
    const next = [...savedRows];
    next.sort((a, b) => {
      const ta = Date.parse(a.created_at || '') || 0;
      const tb = Date.parse(b.created_at || '') || 0;
      if (ta !== tb) return ta - tb;
      return String(a.id).localeCompare(String(b.id));
    });
    return next;
  }, [savedRows]);

  const formatDisplayId = (idx: number) => `FMEA-${String(idx + 1).padStart(2, '0')}`;

  const title = useMemo(() => {
    return fmeaType === 'process' ? 'Process FMEA (PFMEA)' : 'Design FMEA (DFMEA)';
  }, [fmeaType]);

  const loadSaved = async () => {
    if (!projectId) return;
    setLoadingSaved(true);
    setSavedError('');
    try {
      const [comps, fmea] = await Promise.all([
        componentsApi.getByProject(projectId).catch(() => []),
        fmeaApi.getByProject(projectId).catch(() => []),
      ]);
      const map: Record<string, string> = {};
      if (Array.isArray(comps)) {
        for (const c of comps as any[]) {
          if (c?.id && c?.name) map[String(c.id)] = String(c.name);
        }
      }
      setComponentNameById(map);
      setSavedRows(Array.isArray(fmea) ? fmea : []);
    } catch (e: any) {
      setSavedError(e?.message || 'Failed to load saved FMEA rows.');
      setSavedRows([]);
    } finally {
      setLoadingSaved(false);
    }
  };

  const getComponentLabel = (row: FmeaRow) => {
    const id = row.component_id || '';
    if (id && componentNameById[id]) return componentNameById[id];
    const metaName = row.ai_metadata && (row.ai_metadata as any).component_name;
    if (typeof metaName === 'string' && metaName.trim()) return metaName.trim();
    return id || '—';
  };

  const openGenerateVV = async (row: FmeaRow) => {
    setVVRow(row);
    setVVModalOpen(true);
    setVVError(null);
    setVVData(null);
    setVVLoading(true);
    const component = getComponentLabel(row);
    const payload = {
      component: component || '—',
      failure_mode: row.failure_mode || '',
      effect: row.effect || '',
      cause: row.cause || '',
      severity: typeof row.severity === 'number' ? row.severity : 1,
      probability: typeof row.probability === 'number' ? row.probability : 1,
      detection: typeof row.detection === 'number' ? row.detection : 1,
      mitigation: row.mitigation || '',
      residual_severity: row.residual_severity ?? undefined,
      residual_occurrence: row.residual_probability ?? undefined,
      residual_detection: row.residual_detection ?? undefined,
      residual_rpn: row.residual_rpn ?? undefined,
    };
    try {
      const data = await generateVVFromRisk(payload);
      setVVData(data);
    } catch (e: any) {
      const detail = e?.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : e?.message || 'Failed to generate V&V';
      setVVError(msg);
    } finally {
      setVVLoading(false);
    }
  };

  const closeVVModal = () => {
    setVVModalOpen(false);
    setVVData(null);
    setVVError(null);
    setVVRow(null);
  };

  const retryGenerateVV = () => {
    if (vvRow) openGenerateVV(vvRow);
  };

  const seedStarterRows = async () => {
    if (!projectId) return;
    setSavedError('');
    setInfo('');
    setLoadingSaved(true);
    try {
      await projectInitializeApi.run(projectId);
      await loadSaved();
      setInfo('Seeded starter FMEA rows from components.');
    } catch (e: any) {
      setSavedError(e?.message || 'Failed to seed starter rows.');
    } finally {
      setLoadingSaved(false);
    }
  };

  useEffect(() => {
    // Always default to table when entering the page for a project.
    setSavedView('table');
    setDidAutoSeed(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  useEffect(() => {
    // Make older projects self-healing: ensure wizard components have seeded rows
    // and ensure uniqueness rules are applied (>= 5 unique failure modes/component).
    if (!projectId) return;
    if (didAutoSeed) return;
    setDidAutoSeed(true);
    (async () => {
      try {
        await projectInitializeApi.run(projectId);
      } catch {
        // non-blocking; user can still click "Seed starter rows" and see error details
      } finally {
        await loadSaved();
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId, didAutoSeed]);

  // Note: intentionally not persisted to localStorage so "Table" remains the default view.

  const handleGenerate = async () => {
    if (!projectId) return;
    const component = componentDescription.trim();
    if (!component) {
      setError('Please enter a component / process description.');
      return;
    }

    setError('');
    setInfo('');
    setIsGenerating(true);
    try {
      // Legacy AI generator endpoints are mounted under /fmea.
      const endpoint = fmeaType === 'process' ? '/fmea/pfmea/generate' : '/fmea/fmea/generate';
      const res = await api.post(endpoint, { component });
      const data = res.data;
      const raw = data?.fmea_data;
      if (!Array.isArray(raw) || raw.length === 0) {
        throw new Error('No FMEA rows returned from generator.');
      }

      const mapped: GeneratedRow[] = raw.map((r: any, i: number) => {
        const severity = clampScore(r?.severity);
        const occurrence = clampScore(r?.occurrence);
        const detection = clampScore(r?.detection);
        const rpn = Number(r?.rpn) || severity * occurrence * detection;

        const finalSeverity = clampScore(r?.finalSeverity ?? r?.final_severity ?? severity);
        const finalOccurrence = clampScore(r?.finalOccurrence ?? r?.final_occurrence ?? occurrence);
        const finalDetection = clampScore(r?.finalDetection ?? r?.final_detection ?? detection);
        const finalRpn = Number(r?.finalRpn ?? r?.final_rpn) || finalSeverity * finalOccurrence * finalDetection;

        return {
          id: String(r?.id ?? i + 1),
          component: String(r?.component ?? component),
          function: String(r?.function ?? ''),
          failureMode: String(r?.failureMode ?? r?.failure_mode ?? ''),
          potentialEffect: String(r?.potentialEffect ?? r?.effect ?? ''),
          severity,
          potentialCauses: String(r?.potentialCauses ?? r?.cause ?? ''),
          occurrence,
          currentControls: String(r?.currentControls ?? r?.mitigation ?? ''),
          detection,
          rpn,
          recommendedActions: String(r?.recommendedActions ?? ''),
          responsible: String(r?.responsible ?? ''),
          targetDate: String(r?.targetDate ?? ''),
          actionsTaken: String(r?.actionsTaken ?? r?.action_taken ?? ''),
          finalSeverity,
          finalOccurrence,
          finalDetection,
          finalRpn,
        };
      });

      setRows(mapped);
      setInfo(`Generated ${mapped.length} rows. Click “Save to Project” to persist them.`);
    } catch (e: any) {
      setError(e?.message || 'Failed to generate FMEA.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!projectId) return;
    if (!rows.length) {
      setError('No generated rows to save.');
      return;
    }

    setError('');
    setInfo('');
    setIsSaving(true);
    try {
      // Validate project exists / is accessible (also ensures auth is working).
      await projectsApi.getById(projectId);

      // Persist rows to backend project FMEA table.
      // Use limited concurrency to keep the API responsive.
      const results = await mapWithConcurrency(rows, 5, async (row) => {
        return await fmeaApi.create(projectId, {
          failure_mode: row.failureMode,
          effect: row.potentialEffect,
          cause: row.potentialCauses,
          severity: row.severity,
          probability: row.occurrence, // backend uses probability
          detection: row.detection,
          mitigation: row.currentControls || row.recommendedActions || '',
          residual_severity: row.finalSeverity,
          residual_probability: row.finalOccurrence,
          residual_detection: row.finalDetection,
          ai_metadata: {
            source: 'project_fmea_generator',
            generated_type: fmeaType,
            component: row.component,
          },
        });
      });

      setInfo(`Saved ${results.length} FMEA rows to this project.`);
      // Refresh persisted table (so the user immediately sees what was saved).
      await loadSaved();
    } catch (e: any) {
      setError(e?.message || 'Failed to save rows to project.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!projectId) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 text-sm text-gray-700">
        Project ID required. Please select a project first.
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-2xl font-semibold text-gray-900">Project FMEA Generator</div>
          <div className="text-sm text-gray-600 mt-1">
            Generate {title} rows and save them directly into this project.
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => navigate(`/projects/${projectId}/docs/risk_management_core/fmea`)}
            className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
          >
            Open FMEA Doc (Docs)
          </button>
          <button
            type="button"
            onClick={() => navigate(`/projects/${projectId}/documents`)}
            className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50"
          >
            Open Project Documents
          </button>
        </div>
      </div>

      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>
      ) : null}
      {info ? (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-800">{info}</div>
      ) : null}

      <div className="rounded-lg border border-gray-200 bg-white p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">FMEA Type</label>
            <select
              value={fmeaType}
              onChange={(e) => setFmeaType(e.target.value === 'process' ? 'process' : 'design')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isGenerating || isSaving}
            >
              <option value="design">Design FMEA (DFMEA)</option>
              <option value="process">Process FMEA (PFMEA)</option>
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Component / Process Description</label>
            <input
              type="text"
              value={componentDescription}
              onChange={(e) => setComponentDescription(e.target.value)}
              placeholder="Describe the component or process to analyze"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isGenerating || isSaving}
            />
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleGenerate}
            disabled={isGenerating || isSaving || !componentDescription.trim()}
            className="bg-blue-600 text-white px-5 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isGenerating ? 'Generating…' : 'Generate'}
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={!canSave}
            className="bg-green-600 text-white px-5 py-2 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isSaving ? 'Saving…' : 'Save to Project'}
          </button>
        </div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-lg font-semibold text-gray-900">Saved FMEA Rows</div>
            <div className="text-sm text-gray-600">
              These include starter rows created from your Wizard components (at least 5 per component).
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <div className="inline-flex rounded-md border border-gray-300 overflow-hidden">
              <button
                type="button"
                onClick={() => setSavedView('grid')}
                className={`px-3 py-2 text-sm ${
                  savedView === 'grid' ? 'bg-gray-100 text-gray-900' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
                title="Grid view"
              >
                Grid
              </button>
              <button
                type="button"
                onClick={() => setSavedView('table')}
                className={`px-3 py-2 text-sm border-l border-gray-300 ${
                  savedView === 'table' ? 'bg-gray-100 text-gray-900' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
                title="Table view"
              >
                Table
              </button>
            </div>
            <button
              type="button"
              onClick={loadSaved}
              disabled={loadingSaved}
              className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              {loadingSaved ? 'Refreshing…' : 'Refresh'}
            </button>
            <button
              type="button"
              onClick={seedStarterRows}
              disabled={loadingSaved}
              className="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-50"
              title="Runs project initializer to seed starter FMEA rows from components"
            >
              Seed starter rows
            </button>
          </div>
        </div>

        {savedError ? (
          <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{savedError}</div>
        ) : null}

        {!loadingSaved && savedRows.length === 0 ? (
          <div className="mt-4 text-sm text-gray-600">
            No saved rows yet. If you just finished the Wizard, click <b>Refresh</b>. If this is an older project,
            click <b>Seed starter rows</b>.
          </div>
        ) : null}

        {sortedSavedRows.length > 0 && savedView === 'table' ? (
          <FmeaTable
            fmeaRows={sortedSavedRows}
            componentNameById={componentNameById}
            onGenerateVV={openGenerateVV}
          />
        ) : null}

        {sortedSavedRows.length > 0 && savedView === 'grid' ? (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {sortedSavedRows.map((r, idx) => (
              <div key={r.id} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-gray-900">{getComponentLabel(r)}</div>
                    <div className="text-xs text-gray-500 mt-0.5">Row ID: {formatDisplayId(idx)}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500">RPN</div>
                    <div className="text-sm font-bold text-gray-900">{r.rpn ?? '—'}</div>
                  </div>
                </div>

                <div className="mt-3 space-y-2 text-sm">
                  <div>
                    <div className="text-xs font-medium text-gray-500">Failure mode</div>
                    <div className="text-gray-900">{r.failure_mode || '—'}</div>
                  </div>
                  <div>
                    <div className="text-xs font-medium text-gray-500">Effect</div>
                    <div className="text-gray-900">{r.effect || '—'}</div>
                  </div>
                  <div>
                    <div className="text-xs font-medium text-gray-500">Cause</div>
                    <div className="text-gray-900">{r.cause || '—'}</div>
                  </div>
                </div>

                <div className="mt-3 grid grid-cols-4 gap-2 text-center">
                  <div className="rounded-md bg-gray-50 p-2">
                    <div className="text-[11px] text-gray-500">S</div>
                    <div className="text-sm font-semibold text-gray-900">{r.severity ?? '—'}</div>
                  </div>
                  <div className="rounded-md bg-gray-50 p-2">
                    <div className="text-[11px] text-gray-500">P</div>
                    <div className="text-sm font-semibold text-gray-900">{r.probability ?? '—'}</div>
                  </div>
                  <div className="rounded-md bg-gray-50 p-2">
                    <div className="text-[11px] text-gray-500">D</div>
                    <div className="text-sm font-semibold text-gray-900">{r.detection ?? '—'}</div>
                  </div>
                  <div className="rounded-md bg-gray-50 p-2">
                    <div className="text-[11px] text-gray-500">v</div>
                    <div className="text-sm font-semibold text-gray-900">{r.version ?? '—'}</div>
                  </div>
                </div>

                {r.mitigation ? (
                  <div className="mt-3">
                    <div className="text-xs font-medium text-gray-500">Mitigation</div>
                    <div className="text-sm text-gray-900">{r.mitigation}</div>
                  </div>
                ) : null}
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <button
                    type="button"
                    onClick={() => openGenerateVV(r)}
                    className="w-full px-3 py-2 text-sm font-medium text-primary border border-primary rounded-md hover:bg-primary/5"
                  >
                    Generate V&V
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      <GenerateVVModal
        open={vvModalOpen}
        onClose={closeVVModal}
        data={vvData}
        loading={vvLoading}
        error={vvError}
        onRetry={retryGenerateVV}
        projectId={projectId ?? null}
        fmeaRowId={vvRow?.id ?? null}
      />

      {rows.length ? (
        <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between gap-4">
            <div>
              <div className="text-lg font-semibold text-gray-900">{title} Results</div>
              <div className="text-sm text-gray-600">{rows.length} rows</div>
            </div>
          </div>
          <div className="overflow-auto">
            <table className="min-w-[1100px] w-full text-sm">
              <thead className="bg-gray-50 text-gray-700">
                <tr>
                  <th className="text-left px-4 py-3 border-b">Function / Step</th>
                  <th className="text-left px-4 py-3 border-b">Failure Mode</th>
                  <th className="text-left px-4 py-3 border-b">Effect</th>
                  <th className="text-left px-4 py-3 border-b">Cause</th>
                  <th className="text-center px-3 py-3 border-b">S</th>
                  <th className="text-center px-3 py-3 border-b">O/P</th>
                  <th className="text-center px-3 py-3 border-b">D</th>
                  <th className="text-center px-3 py-3 border-b">RPN</th>
                  <th className="text-left px-4 py-3 border-b">Controls / Actions</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r, idx) => (
                  <tr key={`${r.id}-${idx}`} className={idx % 2 ? 'bg-white' : 'bg-gray-50/40'}>
                    <td className="px-4 py-3 border-b align-top">{r.function}</td>
                    <td className="px-4 py-3 border-b align-top">{r.failureMode}</td>
                    <td className="px-4 py-3 border-b align-top">{r.potentialEffect}</td>
                    <td className="px-4 py-3 border-b align-top">{r.potentialCauses}</td>
                    <td className="px-3 py-3 border-b text-center align-top">{r.severity}</td>
                    <td className="px-3 py-3 border-b text-center align-top">{r.occurrence}</td>
                    <td className="px-3 py-3 border-b text-center align-top">{r.detection}</td>
                    <td className="px-3 py-3 border-b text-center align-top">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${getRpnClass(
                          r.rpn
                        )}`}
                        title="RPN (Risk Priority Number)"
                      >
                        {r.rpn}
                      </span>
                    </td>
                    <td className="px-4 py-3 border-b align-top">
                      {r.currentControls || r.recommendedActions || ''}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
}

