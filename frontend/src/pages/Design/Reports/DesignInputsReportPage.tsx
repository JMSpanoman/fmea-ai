import React, { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useProject } from '../../../contexts/ProjectContext';
import api from '../../../axios';
import {
  getDesignInputsReportData,
  exportDesignInputsReportHtml,
  type DesignInputsReportDataResponse,
} from '../../../services/apiService';

type StatusFilter = '' | 'draft' | 'approved' | 'implemented' | 'obsolete';

const DesignInputsReportPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProject } = useProject();

  const finalProjectId = projectId || currentProject?.id;

  const [availableComponents, setAvailableComponents] = useState<any[]>([]);
  const [selectedComponents, setSelectedComponents] = useState<string[]>([]);
  const [manualComponents, setManualComponents] = useState<string[]>([]);
  const [manualInput, setManualInput] = useState('');

  const [status, setStatus] = useState<StatusFilter>('');
  const [includeUnlinked, setIncludeUnlinked] = useState(false);
  const [missingOutput, setMissingOutput] = useState(false);
  const [missingVerification, setMissingVerification] = useState(false);
  const [search, setSearch] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DesignInputsReportDataResponse | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const componentsStr = useMemo(() => {
    const names: string[] = [];
    for (const id of selectedComponents) {
      const c = availableComponents.find((x) => x.id === id);
      if (c?.name) names.push(String(c.name));
    }
    names.push(...manualComponents);
    const uniq = Array.from(new Set(names.map((n) => n.trim()).filter(Boolean)));
    return uniq.length > 0 ? uniq.join(',') : undefined;
  }, [availableComponents, manualComponents, selectedComponents]);

  useEffect(() => {
    const loadComponents = async () => {
      if (!finalProjectId) return;
      try {
        const res = await api.get(`/projects/${finalProjectId}/components`);
        setAvailableComponents(Array.isArray(res.data) ? res.data : []);
      } catch {
        setAvailableComponents([]);
      }
    };
    loadComponents();
  }, [finalProjectId]);

  const addManual = () => {
    const parts = manualInput
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean);
    if (parts.length === 0) return;
    setManualComponents((prev) => Array.from(new Set([...prev, ...parts])));
    setManualInput('');
  };

  const toggleComponent = (id: string) => {
    setSelectedComponents((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const generatePreview = async () => {
    if (!finalProjectId) {
      setError('Please select a project first');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await getDesignInputsReportData(
        finalProjectId,
        componentsStr,
        status || undefined,
        includeUnlinked,
        missingOutput ? true : undefined,
        missingVerification ? true : undefined,
        search || undefined
      );
      setData(res);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load report data');
    } finally {
      setLoading(false);
    }
  };

  const exportHtml = async () => {
    if (!finalProjectId) return;
    try {
      const html = await exportDesignInputsReportHtml(
        finalProjectId,
        componentsStr,
        status || undefined,
        includeUnlinked,
        missingOutput ? true : undefined,
        missingVerification ? true : undefined,
        search || undefined
      );
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Design_Inputs_Documentation_${finalProjectId}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to export HTML');
    }
  };

  if (!finalProjectId) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Select or create a project to continue.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Design Inputs Documentation</h1>
        <p className="text-gray-600">
          Compiles Design Inputs for selected components, traced to upstream Risk Controls.
        </p>
        <p className="text-gray-400 text-xs mt-2 font-mono">Project: {finalProjectId}</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <div>
          <div className="text-sm font-medium text-gray-700 mb-2">Select components</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-52 overflow-auto border border-gray-200 rounded-md p-3">
            {availableComponents.length === 0 ? (
              <div className="text-gray-500 text-sm">No components found (you can still enter names manually).</div>
            ) : (
              availableComponents.map((c) => (
                <label key={c.id} className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={selectedComponents.includes(c.id)}
                    onChange={() => toggleComponent(c.id)}
                  />
                  <span>{c.name}</span>
                </label>
              ))
            )}
          </div>

          <div className="mt-3">
            <div className="text-sm font-medium text-gray-700 mb-2">Or enter component names (comma-separated)</div>
            <div className="flex gap-2">
              <input
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Pump, Valve, Resistor…"
                value={manualInput}
                onChange={(e) => setManualInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addManual();
                  }
                }}
              />
              <button className="bg-gray-200 px-4 py-2 rounded-md hover:bg-gray-300" onClick={addManual}>
                Add
              </button>
            </div>
            {manualComponents.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {manualComponents.map((c) => (
                  <span key={c} className="inline-flex items-center gap-2 px-2 py-1 bg-gray-100 rounded-full text-sm">
                    {c}
                    <button
                      className="text-gray-500 hover:text-gray-800"
                      onClick={() => setManualComponents((prev) => prev.filter((x) => x !== c))}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status filter</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              value={status}
              onChange={(e) => setStatus(e.target.value as StatusFilter)}
            >
              <option value="">All</option>
              <option value="draft">draft</option>
              <option value="approved">approved</option>
              <option value="implemented">implemented</option>
              <option value="obsolete">obsolete</option>
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-700 mt-6">
            <input
              type="checkbox"
              checked={includeUnlinked}
              onChange={(e) => setIncludeUnlinked(e.target.checked)}
            />
            Include unlinked design inputs
          </label>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={missingOutput}
              onChange={(e) => setMissingOutput(e.target.checked)}
            />
            Missing output only
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={missingVerification}
              onChange={(e) => setMissingVerification(e.target.checked)}
            />
            Missing verification only
          </label>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="DI-014, overpressure, shall…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="flex gap-2">
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
            onClick={generatePreview}
            disabled={loading}
          >
            {loading ? 'Generating…' : 'Generate Preview'}
          </button>
          <button
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:bg-gray-400"
            onClick={exportHtml}
            disabled={!data || loading}
            title={!data ? 'Generate preview first' : 'Export HTML'}
          >
            Export HTML
          </button>
        </div>
      </div>

      {data && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex flex-wrap gap-6 text-sm text-gray-700 mb-4">
            <div>
              <span className="font-medium">Design Inputs:</span> {data.counts.design_inputs}
            </div>
            <div>
              <span className="font-medium">Missing output:</span> {data.counts.missing_output}
            </div>
            <div>
              <span className="font-medium">Missing verification:</span> {data.counts.missing_verification}
            </div>
            <div>
              <span className="font-medium">Unlinked requirements:</span> {data.counts.missing_upstream_control}
            </div>
          </div>

          <div className="overflow-auto border border-gray-200 rounded-md">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-3 py-2">DI Key</th>
                  <th className="text-left px-3 py-2">Title</th>
                  <th className="text-left px-3 py-2">Status</th>
                  <th className="text-left px-3 py-2">Upstream</th>
                  <th className="text-left px-3 py-2">Downstream</th>
                  <th className="text-left px-3 py-2">Updated</th>
                  <th className="text-left px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.rows.map((r) => {
                  const isMissing = !r.completeness?.has_upstream_control;
                  const isOpen = !!expanded[r.di_id];
                  const upstreamControlsCount = r.upstream?.risk_controls?.length || 0;
                  const upstreamRisksCount = r.upstream?.risks?.length || 0;
                  const downstreamOutputsCount = r.downstream?.design_outputs?.length || 0;
                  const downstreamVvCount = r.downstream?.vv_tests?.length || 0;
                  return (
                    <React.Fragment key={r.di_id}>
                      <tr className={isMissing ? 'bg-yellow-50' : ''}>
                        <td className="px-3 py-2 font-mono">{r.di_key}</td>
                        <td className="px-3 py-2">{r.title}</td>
                        <td className="px-3 py-2">{r.status}</td>
                        <td className="px-3 py-2">
                          <div className="text-xs text-gray-700">
                            RC: <span className="font-medium">{upstreamControlsCount}</span> · Risks:{' '}
                            <span className="font-medium">{upstreamRisksCount}</span>
                          </div>
                          {!r.completeness?.has_upstream_control && (
                            <div className="text-xs text-yellow-800 font-medium">⚠ Unlinked</div>
                          )}
                        </td>
                        <td className="px-3 py-2">
                          <div className="text-xs text-gray-700">
                            DO: <span className="font-medium">{downstreamOutputsCount}</span> · V&V:{' '}
                            <span className="font-medium">{downstreamVvCount}</span>
                          </div>
                          {!r.completeness?.has_output && (
                            <div className="text-xs text-yellow-800 font-medium">⚠ Missing output</div>
                          )}
                          {!r.completeness?.has_verification && (
                            <div className="text-xs text-yellow-800 font-medium">⚠ Missing verification</div>
                          )}
                        </td>
                        <td className="px-3 py-2 text-xs text-gray-500">
                          {r.updated_at ? new Date(r.updated_at).toLocaleString() : '—'}
                        </td>
                        <td className="px-3 py-2">
                          <button
                            className="text-blue-700 hover:text-blue-900"
                            onClick={() => setExpanded((prev) => ({ ...prev, [r.di_id]: !prev[r.di_id] }))}
                          >
                            {isOpen ? 'Collapse' : 'Expand'}
                          </button>
                        </td>
                      </tr>
                      {isOpen && (
                        <tr>
                          <td colSpan={7} className="px-3 py-3 border-t border-gray-200 bg-white">
                            <div className="space-y-3">
                              <div>
                                <div className="text-xs font-semibold text-gray-600 uppercase">Requirement text</div>
                                <pre className="whitespace-pre-wrap font-mono text-xs bg-gray-50 border border-gray-200 rounded p-3">
                                  {r.requirement_text}
                                </pre>
                              </div>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <div className="text-xs font-semibold text-gray-600 uppercase">Upstream risk controls</div>
                                  {r.upstream?.risk_controls?.length ? (
                                    <ul className="list-disc pl-5 text-sm">
                                      {r.upstream.risk_controls.map((c) => (
                                        <li key={c.control_id}>
                                          <span className="font-mono">{c.control_key}</span> — {c.control_name}
                                        </li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <div className="text-sm text-yellow-800 font-medium">Missing upstream control link</div>
                                  )}
                                </div>
                                <div>
                                  <div className="text-xs font-semibold text-gray-600 uppercase">Upstream risks (optional)</div>
                                  {r.upstream?.risks?.length ? (
                                    <ul className="list-disc pl-5 text-sm">
                                      {r.upstream.risks.map((rk) => (
                                        <li key={rk.risk_item_id}>
                                          <span className="font-mono">{rk.risk_key}</span>
                                          {(rk.hazard || rk.harm) && (
                                            <span className="text-gray-600">
                                              {' '}
                                              — {rk.hazard}
                                              {rk.harm ? ` / ${rk.harm}` : ''}
                                            </span>
                                          )}
                                        </li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <div className="text-sm text-gray-500">None</div>
                                  )}
                                </div>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <div className="text-xs font-semibold text-gray-600 uppercase">Downstream design outputs</div>
                                  {r.downstream?.design_outputs?.length ? (
                                    <ul className="list-disc pl-5 text-sm">
                                      {r.downstream.design_outputs.map((d) => (
                                        <li key={d.id}>
                                          <span className="font-mono">{d.do_key}</span> — {d.title}
                                        </li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <div className="text-sm text-yellow-800 font-medium">Missing design output link</div>
                                  )}
                                </div>
                                <div>
                                  <div className="text-xs font-semibold text-gray-600 uppercase">Downstream V&V tests</div>
                                  {r.downstream?.vv_tests?.length ? (
                                    <ul className="list-disc pl-5 text-sm">
                                      {r.downstream.vv_tests.map((v) => (
                                        <li key={v.id}>
                                          <span className="font-mono">{v.vv_key}</span> — {v.title}
                                        </li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <div className="text-sm text-yellow-800 font-medium">Missing verification evidence</div>
                                  )}
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default DesignInputsReportPage;

