import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { PageHeader } from '../components/ui/PageHeader';
import { RiskAcceptabilityReportResponse, riskAcceptabilityCriteriaApi } from '../services/riskAcceptabilityCriteriaApi';

type SectionItem = {
  key: string;
  value: unknown;
  source_type: string;
  is_user_edited: boolean;
  approved: boolean;
  version: number;
  last_edited_by?: string | null;
  last_edited_at?: string | null;
};

export default function RiskAcceptabilityCriteriaPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RiskAcceptabilityReportResponse | null>(null);
  const [workflowBusy, setWorkflowBusy] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [sectionDrafts, setSectionDrafts] = useState<Record<string, string>>({});
  const [sectionBusyKey, setSectionBusyKey] = useState<string | null>(null);

  const applyReportToForm = useCallback((res: RiskAcceptabilityReportResponse) => {
    setData(res);
    const sections = (res?.report?.sections ?? {}) as Record<string, SectionItem>;
    const nextDrafts: Record<string, string> = {};
    Object.entries(sections).forEach(([key, section]) => {
      nextDrafts[key] = typeof section.value === 'string' ? section.value : JSON.stringify(section.value ?? '', null, 2);
    });
    setSectionDrafts(nextDrafts);
  }, []);

  const loadReport = useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await riskAcceptabilityCriteriaApi.getReport(projectId);
      applyReportToForm(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load report');
    } finally {
      setLoading(false);
    }
  }, [projectId, applyReportToForm]);

  useEffect(() => {
    loadReport();
  }, [loadReport]);

  const handleGenerate = async () => {
    if (!projectId) return;
    setGenerating(true);
    setError(null);
    try {
      const res = await riskAcceptabilityCriteriaApi.generateReport(projectId, false, false);
      applyReportToForm(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateUsingDefaults = async () => {
    if (!projectId) return;
    setGenerating(true);
    setError(null);
    try {
      const res = await riskAcceptabilityCriteriaApi.generateReport(projectId, false, true);
      applyReportToForm(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to regenerate using defaults');
    } finally {
      setGenerating(false);
    }
  };

  if (!projectId) {
    return (
      <div className="p-4">
        <p>Missing project.</p>
        <Button onClick={() => navigate('/projects')}>Back to projects</Button>
      </div>
    );
  }

  const manualItems = data?.report?.manual_review_items ?? [];
  const hasGaps = manualItems.length > 0;
  const sectionMetadata = data?.report?.section_metadata ?? {};
  const readiness = data?.report?.readiness;

  const parseSectionValue = (raw: string): unknown => {
    const trimmed = raw.trim();
    if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
      try {
        return JSON.parse(trimmed);
      } catch {
        return raw;
      }
    }
    return raw;
  };

  const handleSaveSection = async (sectionKey: string) => {
    if (!projectId || !data?.id) return;
    setSectionBusyKey(sectionKey);
    setError(null);
    try {
      await riskAcceptabilityCriteriaApi.updateSection(projectId, data.id, sectionKey, parseSectionValue(sectionDrafts[sectionKey] ?? ''));
      await loadReport();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to save section');
    } finally {
      setSectionBusyKey(null);
    }
  };

  const handleResetSection = async (sectionKey: string) => {
    if (!projectId || !data?.id) return;
    setSectionBusyKey(sectionKey);
    setError(null);
    try {
      await riskAcceptabilityCriteriaApi.resetSectionToDefault(projectId, data.id, sectionKey);
      await loadReport();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to reset section');
    } finally {
      setSectionBusyKey(null);
    }
  };

  const handleApproveSection = async (sectionKey: string) => {
    if (!projectId || !data?.id) return;
    setSectionBusyKey(sectionKey);
    setError(null);
    try {
      await riskAcceptabilityCriteriaApi.approveSection(projectId, data.id, sectionKey, true);
      await loadReport();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to approve section');
    } finally {
      setSectionBusyKey(null);
    }
  };

  const handleWorkflow = async (status: string) => {
    if (!projectId || !data?.id) return;
    setWorkflowBusy(true);
    setError(null);
    try {
      await riskAcceptabilityCriteriaApi.updateWorkflowStatus(projectId, data.id, { status });
      await loadReport();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to update workflow');
    } finally {
      setWorkflowBusy(false);
    }
  };

  const handleComment = async () => {
    if (!projectId || !data?.id || !commentText.trim()) return;
    setWorkflowBusy(true);
    setError(null);
    try {
      await riskAcceptabilityCriteriaApi.addReviewComment(projectId, data.id, { section_key: 'decision_rules', comment: commentText.trim() });
      setCommentText('');
      await loadReport();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to add comment');
    } finally {
      setWorkflowBusy(false);
    }
  };

  const buildExportFilenameBase = () => {
    const datePart = new Date().toISOString().split('T')[0];
    return `Risk_Acceptability_Criteria_${projectId}_${datePart}`;
  };

  const handleExportWord = () => {
    const html = data?.rendered_html;
    if (!html) return;
    const wrappedHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>${html}</body></html>`;
    const blob = new Blob([wrappedHtml], { type: 'application/msword;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${buildExportFilenameBase()}.doc`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleExportPdf = () => {
    const html = data?.rendered_html;
    if (!html) return;
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;
    printWindow.document.open();
    printWindow.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>${buildExportFilenameBase()}</title></head><body>${html}</body></html>`);
    printWindow.document.close();
    setTimeout(() => {
      printWindow.focus();
      printWindow.print();
    }, 250);
  };

  const sections = Object.entries((data?.report?.sections ?? {}) as Record<string, SectionItem>);

  return (
    <div className="p-4 max-w-6xl mx-auto bg-amber-50 min-h-screen">
      <PageHeader
        title="Risk Acceptability Criteria"
        subtitle="ISO 14971–aligned criteria for risk classification and residual risk evaluation"
      />
      <div className="flex flex-wrap gap-2 mb-4">
        <Button variant="secondary" onClick={() => navigate(`/projects/${projectId}/dashboard`)}>
          Back to project
        </Button>
        <Button variant="secondary" onClick={() => navigate(`/projects/${projectId}/docs`)}>
          Documents
        </Button>
        <Button
          variant="primary"
          onClick={handleGenerate}
          disabled={generating || loading}
        >
          {generating ? 'Generating…' : 'Generate new version'}
        </Button>
        <Button
          variant="secondary"
          onClick={handleGenerateUsingDefaults}
          disabled={generating || loading}
        >
          {generating ? 'Generating…' : 'Regenerate using defaults'}
        </Button>
        <Button
          variant="secondary"
          onClick={handleExportPdf}
          disabled={loading || !data?.rendered_html}
        >
          Export PDF
        </Button>
        <Button
          variant="secondary"
          onClick={handleExportWord}
          disabled={loading || !data?.rendered_html}
        >
          Export Word
        </Button>
      </div>

      {error && (
        <Card className="p-4 mb-4 bg-red-50 border-red-200 text-red-800">
          {error}
        </Card>
      )}

      {loading ? (
        <div className="text-gray-600">Loading report…</div>
      ) : (
        <>
          {/* Source / version info */}
          <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-gray-600">
            <span><strong>Version:</strong> {data?.version ?? 0}</span>
            <span><strong>Status:</strong> {data?.status ?? 'draft'}</span>
            {data?.generated_at && (
              <span><strong>Generated:</strong> {new Date(data.generated_at).toLocaleString()}</span>
            )}
            <span className="inline-flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-green-100 text-green-800 text-xs">Approved</span>
              <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 text-xs">Org default</span>
              <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-xs">Draft</span>
              <span className="px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs">Needs review</span>
            </span>
          </div>

          {readiness && (
            <Card className="mb-4 p-4 bg-stone-100 border-stone-300">
              <h2 className="text-base font-semibold text-gray-900 mb-2">Readiness indicators</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-800">
                <div>Completeness: <strong>{readiness.completeness_percentage ?? 0}%</strong></div>
                <div>Approved content: <strong>{readiness.approved_content_percentage ?? 0}%</strong></div>
                <div>Sections requiring review: <strong>{readiness.sections_requiring_manual_review ?? 0}</strong></div>
                <div>Blocked reasons: <strong>{(readiness.blocked_approval_reasons ?? []).length}</strong></div>
              </div>
            </Card>
          )}

          <Card className="mb-4 p-4 bg-amber-100 border-amber-200">
            <h2 className="text-base font-semibold text-gray-900 mb-2">Section metadata badges</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
              {Object.entries(sectionMetadata).map(([key, meta]) => (
                <div key={key} className="p-2 rounded border border-gray-200 bg-gray-50">
                  <div className="font-medium text-gray-900">{key.replaceAll('_', ' ')}</div>
                  <div className="mt-1 flex flex-wrap gap-1">
                    <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 text-xs">{meta.source_type ?? 'unknown'}</span>
                    <span className="px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs">{meta.completeness ?? 'missing'}</span>
                    {meta.requires_human_review && <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-xs">needs review</span>}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="mb-4 p-4 bg-stone-100 border-stone-300">
            <h2 className="text-base font-semibold text-gray-900 mb-2">Editable sections</h2>
            <p className="text-sm text-amber-800 mb-2">Editing this section will override system-generated content.</p>
            <div className="flex flex-wrap gap-2 mb-3">
              <Button variant="secondary" onClick={() => handleWorkflow('in_review')} disabled={workflowBusy}>Move to in_review</Button>
              <Button variant="secondary" onClick={() => handleWorkflow('pending_approval')} disabled={workflowBusy}>Move to pending_approval</Button>
              <Button variant="primary" onClick={() => handleWorkflow('approved')} disabled={workflowBusy}>Approve current version</Button>
              <Button variant="primary" onClick={async () => {
                if (!projectId || !data?.id) return;
                await riskAcceptabilityCriteriaApi.approveAllSections(projectId, data.id);
                await loadReport();
              }}>Approve all sections</Button>
            </div>
            <div className="grid grid-cols-1 gap-3">
              {sections.map(([key, section]) => (
                <div key={key} className="border border-stone-300 rounded p-3 bg-stone-50">
                  <div className="flex flex-wrap justify-between text-xs text-gray-600 mb-2">
                    <span className="font-medium text-gray-900">{key.replaceAll('_', ' ')}</span>
                    <span>Source: {section.source_type}</span>
                    <span>{section.approved ? 'Approved' : 'Draft'}</span>
                    <span>{section.is_user_edited ? 'Edited' : 'Generated'}</span>
                    <span>v{section.version ?? 1}</span>
                  </div>
                  <textarea
                    className="w-full border rounded p-2 text-sm"
                    rows={typeof section.value === 'string' ? 4 : 8}
                    value={sectionDrafts[key] ?? ''}
                    onChange={(e) => setSectionDrafts((prev) => ({ ...prev, [key]: e.target.value }))}
                  />
                  <div className="flex flex-wrap gap-2 mt-2">
                    <Button variant="primary" onClick={() => handleSaveSection(key)} disabled={sectionBusyKey === key}>{sectionBusyKey === key ? 'Saving…' : 'Save'}</Button>
                    <Button variant="secondary" onClick={() => handleResetSection(key)} disabled={sectionBusyKey === key}>Reset to system default</Button>
                    <Button variant="secondary" onClick={() => handleApproveSection(key)} disabled={sectionBusyKey === key || section.approved}>Approve section</Button>
                  </div>
                </div>
              ))}
              <div className="flex gap-2">
                <input className="flex-1 border rounded p-2 text-sm" value={commentText} onChange={(e) => setCommentText(e.target.value)} placeholder="Section review comment (decision_rules)" />
                <Button variant="secondary" onClick={handleComment} disabled={workflowBusy || !commentText.trim()}>Add comment</Button>
              </div>
            </div>
          </Card>

          {/* Required manual review items */}
          {hasGaps && (
            <Card className="mb-4 p-4 border-l-4 border-stone-400 bg-stone-100">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Required manual review items</h2>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-800">
                {manualItems.map((item, idx) => (
                  <li key={idx}>
                    <strong>{item.section ?? 'General'}:</strong> {item.message}
                    {' '}{item.why_it_matters ? <span className="text-gray-700">Why: {item.why_it_matters}. Fix: {item.where_to_fix}. Impact: {item.effect_on_approval_readiness}.</span> : null}
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Rendered report HTML */}
          <Card className="p-0 overflow-hidden bg-amber-100 border-amber-200">
            <div className="p-4 border-b border-amber-200 bg-amber-100 text-sm text-gray-700">
              Report content below is system-generated. Review and approve criteria in your project before use.
            </div>
            <div
              className="p-4 overflow-auto max-h-[70vh] rac-report-content bg-amber-50"
              dangerouslySetInnerHTML={{ __html: data?.rendered_html ?? '<p>No report generated yet. Click “Generate new version” to create one.</p>' }}
            />
          </Card>
        </>
      )}
    </div>
  );
}
