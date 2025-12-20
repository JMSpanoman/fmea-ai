import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { UpstreamLinksPanel } from '../../components/Traceability/UpstreamLinksPanel';
import { getCAPA, CAPA } from '../../api/capas';

const CAPADetailPage: React.FC = () => {
  const { projectId, id } = useParams<{ projectId?: string; id: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const [capa, setCapa] = useState<CAPA | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const finalProjectId = projectId || currentProject?.id || '';

  useEffect(() => {
    if (finalProjectId && id) {
      loadCAPA();
    }
  }, [finalProjectId, id]);

  const loadCAPA = async () => {
    if (!finalProjectId || !id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getCAPA(finalProjectId, id);
      setCapa(data);
    } catch (err: any) {
      console.error('Error loading CAPA:', err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to load CAPA');
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
        <div className="text-text-secondary">Loading CAPA...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-error mb-4">{error}</div>
        <Button onClick={() => loadCAPA()}>Retry</Button>
      </div>
    );
  }

  if (!capa) {
    return (
      <div className="p-6">
        <div className="text-error">CAPA not found</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title={`CAPA: ${capa.id.slice(0, 8)}`}
        breadcrumbs={[
          { label: 'Projects', path: '/projects' },
          { label: 'CAPAs', path: `/capa` },
          { label: capa.id.slice(0, 8), path: '#' },
        ]}
        actions={
          <>
            <Button
              variant="secondary"
              onClick={() => navigate('/capa')}
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
          artifactType="capa"
          artifactId={id}
          onNavigate={(route) => navigate(route)}
        />
      )}

      {/* CAPA Details */}
      <Card>
        <h3 className="text-lg font-semibold mb-4">CAPA Details</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">ID</label>
            <div className="text-text-primary font-mono text-sm">{capa.id}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Root Cause</label>
            <div className="text-text-primary whitespace-pre-wrap">{capa.root_cause}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">CAPA Plan</label>
            <div className="text-text-primary whitespace-pre-wrap">{capa.capa_plan}</div>
          </div>
          {capa.effectiveness_check && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Effectiveness Check</label>
              <div className="text-text-primary whitespace-pre-wrap">{capa.effectiveness_check}</div>
            </div>
          )}
          {capa.linked_risk_ids && capa.linked_risk_ids.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Linked Risk IDs</label>
              <div className="flex flex-wrap gap-2">
                {capa.linked_risk_ids.map((riskId) => (
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
              {new Date(capa.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default CAPADetailPage;

