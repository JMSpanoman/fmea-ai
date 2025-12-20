import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { UpstreamLinksPanel } from '../../components/Traceability/UpstreamLinksPanel';
import { getVvTest, VVTest } from '../../api/vvTests';

const VVTestDetailPage: React.FC = () => {
  const { projectId, id } = useParams<{ projectId?: string; id: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const [vvTest, setVvTest] = useState<VVTest | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const finalProjectId = projectId || currentProject?.id || '';

  useEffect(() => {
    if (finalProjectId && id) {
      loadVvTest();
    }
  }, [finalProjectId, id]);

  const loadVvTest = async () => {
    if (!finalProjectId || !id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getVvTest(finalProjectId, id);
      setVvTest(data);
    } catch (err: any) {
      console.error('Error loading V&V test:', err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to load V&V test');
    } finally {
      setLoading(false);
    }
  };

  if (!finalProjectId) {
    return (
      <div className="p-6">
        <div className="text-error">Project ID required. Please select a project first.</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-text-secondary">Loading V&V test...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-error mb-4">{error}</div>
        <Button onClick={() => loadVvTest()}>Retry</Button>
      </div>
    );
  }

  if (!vvTest) {
    return (
      <div className="p-6">
        <div className="text-error">V&V test not found</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title={`V&V Test: ${vvTest.id.slice(0, 8)}`}
        breadcrumbs={[
          { label: 'Projects', path: '/projects' },
          { label: 'V&V Tests', path: `/projects/${finalProjectId}/vv-tests` },
          { label: vvTest.id.slice(0, 8), path: '#' },
        ]}
        actions={
          <>
            <Button
              variant="secondary"
              onClick={() => {
                const basePath = projectId ? `/projects/${finalProjectId}` : '';
                navigate(`${basePath}/vv-tests`);
              }}
            >
              Back to List
            </Button>
          </>
        }
      />

      {/* Upstream Links Panel */}
      {finalProjectId && id && (
        <UpstreamLinksPanel
          projectId={finalProjectId}
          artifactType="vv_test"
          artifactId={id}
          onNavigate={(route) => navigate(route)}
        />
      )}

      {/* V&V Test Details */}
      <Card>
        <h3 className="text-lg font-semibold mb-4">V&V Test Details</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">ID</label>
            <div className="text-text-primary font-mono text-sm">{vvTest.id}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Test Method</label>
            <div className="text-text-primary whitespace-pre-wrap">{vvTest.test_method}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Acceptance Criteria</label>
            <div className="text-text-primary whitespace-pre-wrap">{vvTest.acceptance_criteria}</div>
          </div>
          {vvTest.rationale && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Rationale</label>
              <div className="text-text-primary whitespace-pre-wrap">{vvTest.rationale}</div>
            </div>
          )}
          {vvTest.design_output_id && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Linked Design Output</label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate(`/projects/${finalProjectId}/design-outputs/${vvTest.design_output_id}`)}
              >
                {vvTest.design_output_id.slice(0, 8)}
              </Button>
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Created</label>
            <div className="text-text-primary">
              {new Date(vvTest.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default VVTestDetailPage;

