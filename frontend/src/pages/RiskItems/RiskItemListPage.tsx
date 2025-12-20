import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { DataTable } from '../../components/ui/DataTable';
import { Button } from '../../components/ui/Button';
import { Input, Textarea } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import { Badge } from '../../components/ui/Badge';
import {
  listRiskItems,
  createRiskItem,
  RiskItem,
  RiskItemCreate,
} from '../../api/riskItems';

const RiskItemListPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  
  const [riskItems, setRiskItems] = useState<RiskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filters, setFilters] = useState<{ status?: string; category?: string; search?: string }>({});
  
  // Create form state
  const [formData, setFormData] = useState<Partial<RiskItemCreate>>({
    title: '',
    hazard: '',
    hazardous_situation: '',
    harm: '',
    failure_mode: '',
    severity: undefined,
    probability_of_harm: undefined,
    occurrence: undefined,
    detection: undefined,
    risk_rationale: '',
  });
  
  const finalProjectId = projectId || currentProject?.id || '';

  useEffect(() => {
    if (finalProjectId) {
      loadRiskItems();
    }
  }, [finalProjectId, filters]);

  const loadRiskItems = async () => {
    if (!finalProjectId) return;
    
    try {
      setLoading(true);
      const items = await listRiskItems(finalProjectId, filters);
      
      // Apply search filter if provided
      let filtered = items;
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        filtered = items.filter(item => 
          item.title?.toLowerCase().includes(searchLower) ||
          item.current_version?.hazard?.toLowerCase().includes(searchLower) ||
          item.current_version?.failure_mode?.toLowerCase().includes(searchLower)
        );
      }
      
      setRiskItems(filtered);
    } catch (error) {
      console.error('Error loading risk items:', error);
      alert('Failed to load risk items');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!finalProjectId || !formData.title || !formData.hazard) {
      alert('Title and Hazard are required');
      return;
    }

    try {
      const newItem = await createRiskItem(finalProjectId, {
        ...formData,
        project_id: finalProjectId,
      } as RiskItemCreate);
      
      setShowCreateModal(false);
      setFormData({
        title: '',
        hazard: '',
        hazardous_situation: '',
        harm: '',
        failure_mode: '',
        severity: undefined,
        probability_of_harm: undefined,
        occurrence: undefined,
        detection: undefined,
        risk_rationale: '',
      });
      
      // Navigate to detail page
      if (projectId) {
        navigate(`/projects/${finalProjectId}/risk-items/${newItem.id}`);
      } else {
        navigate(`/risk-items/${newItem.id}`);
      }
    } catch (error) {
      console.error('Error creating risk item:', error);
      alert('Failed to create risk item');
    }
  };

  const getRiskScoreBadge = (item: RiskItem) => {
    const score = item.current_version?.risk_score || item.risk_score;
    if (!score) return null;
    
    let variant: 'primary' | 'secondary' | 'danger' = 'secondary';
    if (score >= 700) variant = 'danger';
    else if (score >= 400) variant = 'primary';
    
    return (
      <Badge variant={variant}>
        {score} ({item.current_version?.risk_level || item.risk_level || 'N/A'})
      </Badge>
    );
  };

  const columns = [
    {
      key: 'title',
      header: 'Risk Key',
      render: (item: RiskItem) => (
        <div>
          <div className="font-medium text-text-primary">{item.title}</div>
          {item.id && (
            <div className="text-xs text-text-secondary mt-1">ID: {item.id.substring(0, 8)}...</div>
          )}
        </div>
      ),
    },
    {
      key: 'hazard',
      header: 'Hazard',
      render: (item: RiskItem) => (
        <div className="text-sm text-text-secondary">
          {item.current_version?.hazard || '-'}
        </div>
      ),
    },
    {
      key: 'failure_mode',
      header: 'Failure Mode',
      render: (item: RiskItem) => (
        <div className="text-sm text-text-secondary">
          {item.current_version?.failure_mode || '-'}
        </div>
      ),
    },
    {
      key: 'risk_score',
      header: 'Risk Score',
      render: (item: RiskItem) => getRiskScoreBadge(item),
    },
    {
      key: 'acceptability',
      header: 'Acceptability / Status',
      render: (item: RiskItem) => (
        <div className="flex flex-col gap-1">
          {item.current_version?.risk_acceptability && (
            <Badge variant={item.current_version.risk_acceptability === 'acceptable' ? 'primary' : 'secondary'}>
              {item.current_version.risk_acceptability}
            </Badge>
          )}
          <Badge variant={item.status === 'closed' ? 'secondary' : 'primary'}>
            {item.status}
          </Badge>
        </div>
      ),
    },
    {
      key: 'updated',
      header: 'Updated',
      render: (item: RiskItem) => {
        const date = item.current_version?.created_at || item.updated_at || item.created_at;
        return date ? new Date(date).toLocaleDateString() : '-';
      },
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (item: RiskItem) => (
        <Button
          variant="secondary"
          size="sm"
          onClick={() => {
            const basePath = projectId ? `/projects/${finalProjectId}` : '';
            navigate(`${basePath}/risk-items/${item.id}`);
          }}
        >
          View
        </Button>
      ),
    },
  ];

  if (!finalProjectId) {
    return (
      <div className="p-6">
        <Card>
          <div className="text-center py-8 text-text-secondary">
            Please select a project first
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6">
      <PageHeader
        title="SmartQS Risk Items"
        description="Manage risk items with ISO 14971 compliance"
        actions={
          <Button onClick={() => setShowCreateModal(true)}>
            Create Risk Item
          </Button>
        }
      />

      {/* Filters */}
      <Card className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Input
            placeholder="Search..."
            value={filters.search || ''}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          />
          <select
            className="px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary"
            value={filters.status || ''}
            onChange={(e) => setFilters({ ...filters, status: e.target.value || undefined })}
          >
            <option value="">All Status</option>
            <option value="open">Open</option>
            <option value="mitigated">Mitigated</option>
            <option value="closed">Closed</option>
            <option value="accepted">Accepted</option>
          </select>
          <select
            className="px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary"
            value={filters.category || ''}
            onChange={(e) => setFilters({ ...filters, category: e.target.value || undefined })}
          >
            <option value="">All Categories</option>
            <option value="Safety">Safety</option>
            <option value="Quality">Quality</option>
            <option value="Financial">Financial</option>
            <option value="Compliance">Compliance</option>
          </select>
          <Button
            variant="ghost"
            onClick={() => setFilters({})}
          >
            Clear Filters
          </Button>
        </div>
      </Card>

      {/* Table */}
      {loading ? (
        <Card>
          <div className="text-center py-8 text-text-secondary">Loading...</div>
        </Card>
      ) : (
        <DataTable
          data={riskItems}
          columns={columns}
          emptyMessage="No risk items found. Create one to get started."
        />
      )}

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create Risk Item"
        size="lg"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate}>Create</Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Title *"
            value={formData.title || ''}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Enter risk item title"
          />
          
          <Textarea
            label="Hazard *"
            value={formData.hazard || ''}
            onChange={(e) => setFormData({ ...formData, hazard: e.target.value })}
            placeholder="Potential source of harm"
            rows={3}
          />
          
          <Textarea
            label="Hazardous Situation"
            value={formData.hazardous_situation || ''}
            onChange={(e) => setFormData({ ...formData, hazardous_situation: e.target.value })}
            placeholder="Circumstance in which people/property are exposed to hazards"
            rows={2}
          />
          
          <Textarea
            label="Harm"
            value={formData.harm || ''}
            onChange={(e) => setFormData({ ...formData, harm: e.target.value })}
            placeholder="Physical injury or damage to health/property"
            rows={2}
          />
          
          <Input
            label="Failure Mode"
            value={formData.failure_mode || ''}
            onChange={(e) => setFormData({ ...formData, failure_mode: e.target.value })}
            placeholder="FMEA-style failure mode"
          />
          
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Severity (1-10)"
              type="number"
              min="1"
              max="10"
              value={formData.severity || ''}
              onChange={(e) => setFormData({ ...formData, severity: parseInt(e.target.value) || undefined })}
            />
            
            <Input
              label="Probability of Harm (1-10)"
              type="number"
              min="1"
              max="10"
              value={formData.probability_of_harm || ''}
              onChange={(e) => setFormData({ ...formData, probability_of_harm: parseInt(e.target.value) || undefined })}
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Occurrence (1-10) - Optional"
              type="number"
              min="1"
              max="10"
              value={formData.occurrence || ''}
              onChange={(e) => setFormData({ ...formData, occurrence: parseInt(e.target.value) || undefined })}
            />
            
            <Input
              label="Detection (1-10) - Optional"
              type="number"
              min="1"
              max="10"
              value={formData.detection || ''}
              onChange={(e) => setFormData({ ...formData, detection: parseInt(e.target.value) || undefined })}
            />
          </div>
          
          <Textarea
            label="Risk Rationale"
            value={formData.risk_rationale || ''}
            onChange={(e) => setFormData({ ...formData, risk_rationale: e.target.value })}
            placeholder="Rationale for risk acceptability decision"
            rows={3}
          />
        </div>
      </Modal>
    </div>
  );
};

export default RiskItemListPage;

