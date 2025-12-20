import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { UpstreamLinksPanel } from '../../components/Traceability/UpstreamLinksPanel';
import { getDesignOutput, DesignOutput } from '../../api/designOutputs';

const DesignOutputDetailPage: React.FC = () => {
  const { projectId, id } = useParams<{ projectId?: string; id: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const [designOutput, setDesignOutput] = useState<DesignOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const finalProjectId = projectId || currentProject?.id || '';

  useEffect(() => {
    if (finalProjectId && id) {
      loadDesignOutput();
    }
  }, [finalProjectId, id]);

  const loadDesignOutput = async () => {
    if (!finalProjectId || !id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getDesignOutput(finalProjectId, id);
      setDesignOutput(data);
    } catch (err: any) {
      console.error('Error loading design output:', err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to load design output');
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
        <div className="text-text-secondary">Loading design output...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-error mb-4">{error}</div>
        <Button onClick={() => loadDesignOutput()}>Retry</Button>
      </div>
    );
  }

  if (!designOutput) {
    return (
      <div className="p-6">
        <div className="text-error">Design output not found</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title={`Design Output: ${designOutput.id.slice(0, 8)}`}
        breadcrumbs={[
          { label: 'Projects', path: '/projects' },
          { label: 'Design Outputs', path: `/projects/${finalProjectId}/design-outputs` },
          { label: designOutput.id.slice(0, 8), path: '#' },
        ]}
        actions={
          <>
            <Button
              variant="secondary"
              onClick={() => {
                const basePath = projectId ? `/projects/${finalProjectId}` : '';
                navigate(`${basePath}/design-outputs`);
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
          artifactType="design_output"
          artifactId={id}
          onNavigate={(route) => navigate(route)}
        />
      )}

      {/* Design Output Details */}
      <Card>
        <h3 className="text-lg font-semibold mb-4">Design Output Details</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">ID</label>
            <div className="text-text-primary font-mono text-sm">{designOutput.id}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Source</label>
            <div className="text-text-primary">{designOutput.source}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Output/Text</label>
            <div className="text-text-primary whitespace-pre-wrap">{designOutput.text}</div>
          </div>
          {designOutput.linked_input_id && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Linked Design Input</label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate(`/projects/${finalProjectId}/design-inputs/${designOutput.linked_input_id}`)}
              >
                {designOutput.linked_input_id.slice(0, 8)}
              </Button>
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Created</label>
            <div className="text-text-primary">
              {new Date(designOutput.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default DesignOutputDetailPage;

