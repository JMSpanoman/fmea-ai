import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import {
  riskAcceptabilityCriteriaApi,
  RiskAcceptabilityReportResponse,
} from '../services/riskAcceptabilityCriteriaApi';

export default function RiskAcceptabilityCriteriaPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RiskAcceptabilityReportResponse | null>(null);

  const loadReport = useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await riskAcceptabilityCriteriaApi.getReport(projectId);
      setData(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load report');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadReport();
  }, [loadReport]);

  const handleGenerate = async () => {
    if (!projectId) return;
    setGenerating(true);
    setError(null);
    try {
      const res = await riskAcceptabilityCriteriaApi.generateReport(projectId, false);
      setData(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to generate report');
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

  return (
    <div className="p-4 max-w-6xl mx-auto bg-white min-h-screen">
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

          {/* Required manual review items */}
          {hasGaps && (
            <Card className="mb-4 p-4 border-l-4 border-amber-500 bg-amber-50">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Required manual review items</h2>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-800">
                {manualItems.map((item, idx) => (
                  <li key={idx}>
                    <strong>{item.section ?? 'General'}:</strong> {item.message}
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Rendered report HTML */}
          <Card className="p-0 overflow-hidden">
            <div className="p-4 border-b border-gray-200 bg-gray-50 text-sm text-gray-600">
              Report content below is system-generated. Review and approve criteria in your project before use.
            </div>
            <div
              className="p-4 overflow-auto max-h-[70vh] rac-report-content"
              dangerouslySetInnerHTML={{ __html: data?.rendered_html ?? '<p>No report generated yet. Click “Generate new version” to create one.</p>' }}
            />
          </Card>
        </>
      )}
    </div>
  );
}
