import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { UpstreamLinksPanel } from '../../components/Traceability/UpstreamLinksPanel';
import { getChangeControl, ChangeControl } from '../../api/changeControls';

const ChangeControlDetailPage: React.FC = () => {
  const { projectId, id } = useParams<{ projectId?: string; id: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const [changeControl, setChangeControl] = useState<ChangeControl | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const finalProjectId = projectId || currentProject?.id || '';

  useEffect(() => {
    if (finalProjectId && id) {
      loadChangeControl();
    }
  }, [finalProjectId, id]);

  const loadChangeControl = async () => {
    if (!finalProjectId || !id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getChangeControl(finalProjectId, id);
      setChangeControl(data);
    } catch (err: any) {
      console.error('Error loading change control:', err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to load change control');
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
        <div className="text-text-secondary">Loading change control...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-error mb-4">{error}</div>
        <Button onClick={() => loadChangeControl()}>Retry</Button>
      </div>
    );
  }

  if (!changeControl) {
    return (
      <div className="p-6">
        <div className="text-error">Change control not found</div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'closed':
      case 'approved':
        return 'success';
      case 'in_review':
        return 'warning';
      case 'open':
        return 'info';
      default:
        return 'secondary';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title={`Change Control: ${changeControl.title}`}
        breadcrumbs={[
          { label: 'Projects', path: '/projects' },
          { label: 'Change Controls', path: `/change-control` },
          { label: changeControl.id.slice(0, 8), path: '#' },
        ]}
        actions={
          <>
            <Button
              variant="secondary"
              onClick={() => navigate('/change-control')}
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
          artifactType="change_control"
          artifactId={id}
          onNavigate={(route) => navigate(route)}
        />
      )}

      {/* Change Control Details */}
      <Card>
        <h3 className="text-lg font-semibold mb-4">Change Control Details</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">ID</label>
            <div className="text-text-primary font-mono text-sm">{changeControl.id}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Title</label>
            <div className="text-text-primary font-semibold">{changeControl.title}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Status</label>
            <Badge variant={getStatusColor(changeControl.status)}>
              {changeControl.status}
            </Badge>
          </div>
          {changeControl.description && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Description</label>
              <div className="text-text-primary whitespace-pre-wrap">{changeControl.description}</div>
            </div>
          )}
          {changeControl.reason && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Reason</label>
              <div className="text-text-primary whitespace-pre-wrap">{changeControl.reason}</div>
            </div>
          )}
          {changeControl.linked_risk_ids && changeControl.linked_risk_ids.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Linked Risk IDs</label>
              <div className="flex flex-wrap gap-2">
                {changeControl.linked_risk_ids.map((riskId) => (
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
              {new Date(changeControl.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ChangeControlDetailPage;

