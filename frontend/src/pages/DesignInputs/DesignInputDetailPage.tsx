import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { UpstreamLinksPanel } from '../../components/Traceability/UpstreamLinksPanel';
import { getDesignInput, DesignInput } from '../../api/designInputs';

const DesignInputDetailPage: React.FC = () => {
  const { projectId, id } = useParams<{ projectId?: string; id: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const [designInput, setDesignInput] = useState<DesignInput | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const finalProjectId = projectId || currentProject?.id || '';

  useEffect(() => {
    if (finalProjectId && id) {
      loadDesignInput();
    }
  }, [finalProjectId, id]);

  const loadDesignInput = async () => {
    if (!finalProjectId || !id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getDesignInput(finalProjectId, id);
      setDesignInput(data);
    } catch (err: any) {
      console.error('Error loading design input:', err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to load design input');
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
        <div className="text-text-secondary">Loading design input...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-error mb-4">{error}</div>
        <Button onClick={() => loadDesignInput()}>Retry</Button>
      </div>
    );
  }

  if (!designInput) {
    return (
      <div className="p-6">
        <div className="text-error">Design input not found</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title={`Design Input: ${designInput.id.slice(0, 8)}`}
        breadcrumbs={[
          { label: 'Projects', path: '/projects' },
          { label: 'Design Inputs', path: `/projects/${finalProjectId}/design-inputs` },
          { label: designInput.id.slice(0, 8), path: '#' },
        ]}
        actions={
          <>
            <Button
              variant="secondary"
              onClick={() => {
                const basePath = projectId ? `/projects/${finalProjectId}` : '';
                navigate(`${basePath}/design-inputs`);
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
          artifactType="design_input"
          artifactId={id}
          onNavigate={(route) => navigate(route)}
        />
      )}

      {/* Design Input Details */}
      <Card>
        <h3 className="text-lg font-semibold mb-4">Design Input Details</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">ID</label>
            <div className="text-text-primary font-mono text-sm">{designInput.id}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Source</label>
            <div className="text-text-primary">{designInput.source}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Requirement/Text</label>
            <div className="text-text-primary whitespace-pre-wrap">{designInput.text}</div>
          </div>
          {designInput.linked_risk_ids && designInput.linked_risk_ids.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Linked Risk IDs</label>
              <div className="flex flex-wrap gap-2">
                {designInput.linked_risk_ids.map((riskId) => (
                  <Button
                    key={riskId}
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate(`/projects/${finalProjectId}/risk-items/${riskId}`)}
                  >
                    {riskId.slice(0, 8)}
                  </Button>
                ))}
              </div>
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Created</label>
            <div className="text-text-primary">
              {new Date(designInput.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default DesignInputDetailPage;

