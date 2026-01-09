import React, { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useProject } from '../../../contexts/ProjectContext';
import api from '../../../axios';
import {
  getVVEvidenceReportData,
  exportVVEvidenceReportHtml,
  type VVEvidenceReportDataResponse,
} from '../../../services/apiService';

type TestTypeFilter = '' | 'verification' | 'validation';

const VVEvidenceReportPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProject } = useProject();

  const finalProjectId = projectId || currentProject?.id;

  const [availableComponents, setAvailableComponents] = useState<any[]>([]);
  const [selectedComponents, setSelectedComponents] = useState<string[]>([]);
  const [manualComponents, setManualComponents] = useState<string[]>([]);
  const [manualInput, setManualInput] = useState('');

  const [testType, setTestType] = useState<TestTypeFilter>('');
  const [status, setStatus] = useState<string>('');
  const [unlinkedOnly, setUnlinkedOnly] = useState(false);
  const [missingDoLink, setMissingDoLink] = useState(false);
  const [missingAc, setMissingAc] = useState(false);
  const [search, setSearch] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<VVEvidenceReportDataResponse | null>(null);
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
      const res = await getVVEvidenceReportData(
        finalProjectId,
        componentsStr,
        testType || undefined,
        status || undefined,
        unlinkedOnly ? true : undefined,
        missingAc ? true : undefined,
        missingDoLink ? true : undefined,
        search || undefined
      );
      setData(res);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load V&V evidence report');
    } finally {
      setLoading(false);
    }
  };

  const exportHtml = async () => {
    if (!finalProjectId) return;
    try {
      const html = await exportVVEvidenceReportHtml(
        finalProjectId,
        componentsStr,
        testType || undefined,
        status || undefined,
        unlinkedOnly ? true : undefined,
        missingAc ? true : undefined,
        missingDoLink ? true : undefined,
        search || undefined
      );
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `VV_Evidence_Report_${finalProjectId}.html`;
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

  const strengthBadge = (s: string) => {
    if (s === 'preferred') return 'bg-green-100 text-green-800';
    if (s === 'allowed') return 'bg-blue-100 text-blue-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  return (
    <div className="p-6 space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">V&V Evidence Report</h1>
        <p className="text-gray-600">
          Component-scoped evidence that requirements/outputs/controls were verified or validated via trace links.
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

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              value={testType}
              onChange={(e) => setTestType(e.target.value as TestTypeFilter)}
            >
              <option value="">All</option>
              <option value="verification">verification</option>
              <option value="validation">validation</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <input
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="planned / passed / failed …"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="V-007, overpressure, pressure…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" checked={unlinkedOnly} onChange={(e) => setUnlinkedOnly(e.target.checked)} />
            Unlinked tests only
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" checked={missingDoLink} onChange={(e) => setMissingDoLink(e.target.checked)} />
            Missing Design Output link
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" checked={missingAc} onChange={(e) => setMissingAc(e.target.checked)} />
            Missing acceptance criteria
          </label>
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
              <span className="font-medium">Tests:</span> {data.counts.tests}
            </div>
            <div>
              <span className="font-medium">Unlinked:</span> {data.counts.unlinked}
            </div>
            <div>
              <span className="font-medium">Missing DO link:</span> {data.counts.missing_design_output_link}
            </div>
            <div>
              <span className="font-medium">Missing AC:</span> {data.counts.missing_acceptance_criteria}
            </div>
          </div>

          <div className="overflow-auto border border-gray-200 rounded-md">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-3 py-2">V Key</th>
                  <th className="text-left px-3 py-2">Title</th>
                  <th className="text-left px-3 py-2">Type</th>
                  <th className="text-left px-3 py-2">Status</th>
                  <th className="text-left px-3 py-2">Strength</th>
                  <th className="text-left px-3 py-2">Upstream</th>
                  <th className="text-left px-3 py-2">Updated</th>
                  <th className="text-left px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.rows.map((r) => {
                  const isOpen = !!expanded[r.vv_test_id];
                  const doCount = r.upstream?.design_outputs?.length || 0;
                  const diCount = r.upstream?.design_inputs?.length || 0;
                  const rcCount = r.upstream?.risk_controls?.length || 0;
                  const riskCount = r.upstream?.risk_items?.length || 0;
                  return (
                    <React.Fragment key={r.vv_test_id}>
                      <tr className={!r.completeness?.has_design_output_link ? 'bg-yellow-50' : ''}>
                        <td className="px-3 py-2 font-mono">{r.vv_key}</td>
                        <td className="px-3 py-2">{r.title}</td>
                        <td className="px-3 py-2">{r.test_type}</td>
                        <td className="px-3 py-2">{r.status}</td>
                        <td className="px-3 py-2">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${strengthBadge(r.evidence_strength)}`}>
                            {r.evidence_strength}
                          </span>
                        </td>
                        <td className="px-3 py-2">
                          <div className="text-xs text-gray-700">
                            DO:{' '}
                            <span className="font-medium">{doCount}</span> · DI:{' '}
                            <span className="font-medium">{diCount}</span> · RC:{' '}
                            <span className="font-medium">{rcCount}</span> · Risk:{' '}
                            <span className="font-medium">{riskCount}</span>
                          </div>
                          {!r.completeness?.has_design_output_link && (
                            <div className="text-xs text-yellow-800 font-medium">⚠ Missing DO link</div>
                          )}
                          {!r.completeness?.has_acceptance_criteria && (
                            <div className="text-xs text-yellow-800 font-medium">⚠ Missing AC</div>
                          )}
                          {!r.completeness?.has_upstream_links && (
                            <div className="text-xs text-yellow-800 font-medium">⚠ Unlinked</div>
                          )}
                        </td>
                        <td className="px-3 py-2 text-xs text-gray-500">
                          {r.updated_at ? new Date(r.updated_at).toLocaleString() : '—'}
                        </td>
                        <td className="px-3 py-2">
                          <button
                            className="text-blue-700 hover:text-blue-900"
                            onClick={() => setExpanded((prev) => ({ ...prev, [r.vv_test_id]: !prev[r.vv_test_id] }))}
                          >
                            {isOpen ? 'Collapse' : 'Expand'}
                          </button>
                        </td>
                      </tr>
                      {isOpen && (
                        <tr>
                          <td colSpan={8} className="px-3 py-3 border-t border-gray-200 bg-white">
                            <div className="space-y-3">
                              <div>
                                <div className="text-xs font-semibold text-gray-600 uppercase">Acceptance criteria</div>
                                <pre className="whitespace-pre-wrap font-mono text-xs bg-gray-50 border border-gray-200 rounded p-3">
                                  {r.acceptance_criteria}
                                </pre>
                              </div>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <div className="text-xs font-semibold text-gray-600 uppercase">Upstream design outputs</div>
                                  {r.upstream?.design_outputs?.length ? (
                                    <ul className="list-disc pl-5 text-sm">
                                      {r.upstream.design_outputs.map((d) => (
                                        <li key={d.id}>
                                          <span className="font-mono">{d.do_key}</span> — {d.title}
                                        </li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <div className="text-sm text-yellow-800 font-medium">Missing DO link evidence</div>
                                  )}
                                </div>
                                <div>
                                  <div className="text-xs font-semibold text-gray-600 uppercase">Upstream design inputs</div>
                                  {r.upstream?.design_inputs?.length ? (
                                    <ul className="list-disc pl-5 text-sm">
                                      {r.upstream.design_inputs.map((d) => (
                                        <li key={d.id}>
                                          <span className="font-mono">{d.di_key}</span> — {d.title}
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
                                  <div className="text-xs font-semibold text-gray-600 uppercase">Upstream risk controls</div>
                                  {r.upstream?.risk_controls?.length ? (
                                    <ul className="list-disc pl-5 text-sm">
                                      {r.upstream.risk_controls.map((c) => (
                                        <li key={c.id}>
                                          <span className="font-mono">{c.control_key}</span> — {c.name}
                                        </li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <div className="text-sm text-gray-500">None</div>
                                  )}
                                </div>
                                <div>
                                  <div className="text-xs font-semibold text-gray-600 uppercase">Upstream risks</div>
                                  {r.upstream?.risk_items?.length ? (
                                    <ul className="list-disc pl-5 text-sm">
                                      {r.upstream.risk_items.map((rk) => (
                                        <li key={rk.id}>
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

export default VVEvidenceReportPage;

