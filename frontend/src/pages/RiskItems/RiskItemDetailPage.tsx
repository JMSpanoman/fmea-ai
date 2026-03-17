import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../../contexts/ProjectContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input, Textarea } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import { Badge } from '../../components/ui/Badge';
import { Drawer } from '../../components/ui/Drawer';
import { DataTable } from '../../components/ui/DataTable';
import { useToast } from '../../components/ui/Toast';
import { DownstreamLinksPanel } from '../../components/Traceability/DownstreamLinksPanel';
import { ConnectedGraphView } from '../../components/Traceability/ConnectedGraphView';
import { getArtifactRoute } from '../../utils/traceRoutes';
import { exportRiskEvidenceHTML, exportRiskEvidencePDF, RiskEvidenceData } from '../../utils/riskEvidenceExport';
import {
  getRiskItem,
  updateRiskItem,
  createRiskVersion,
  listRiskVersions,
  getRiskVersion,
  approveRiskVersion,
  listRiskControls,
  createRiskControl,
  patchRiskControl,
  deleteRiskControl,
  listRiskLinks,
  createRiskLink,
  getAIRiskSuggestions,
  updateAIEventDisposition,
  getRiskItemAIEvents,
  handoffControlToDesign,
  handoffRiskToCAPA,
  handoffRiskVersionToChange,
  AIRiskSuggestions,
  AIEvent,
  RiskItem,
  RiskItemVersion,
  RiskControl,
  RiskItemUpdate,
  RiskItemVersionCreate,
  RiskControlCreate,
  RiskControlUpdate,
  RiskItemApprovalRequest,
  TraceLink,
} from '../../api/riskItems';
import { generateVVFromRisk } from '../../services/vvFromRiskApi';
import { GenerateVVModal } from '../../components/VV/GenerateVVModal';

type TabType = 'current' | 'controls' | 'traceability' | 'versions' | 'approval' | 'graph';

const RiskItemDetailPage: React.FC = () => {
  const { projectId, riskItemId } = useParams<{ projectId: string; riskItemId: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState<TabType>('current');
  const [riskItem, setRiskItem] = useState<RiskItem | null>(null);
  const [versions, setVersions] = useState<RiskItemVersion[]>([]);
  const [controls, setControls] = useState<RiskControl[]>([]);
  const [links, setLinks] = useState<{ from: TraceLink[]; to: TraceLink[] }>({ from: [], to: [] });
  const [loading, setLoading] = useState(true);
  
  // Form states
  const [currentVersionData, setCurrentVersionData] = useState<Partial<RiskItemUpdate>>({});
  const [showControlModal, setShowControlModal] = useState(false);
  const [selectedControl, setSelectedControl] = useState<RiskControl | null>(null);
  const [controlFormData, setControlFormData] = useState<Partial<RiskControlCreate>>({});
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [linkFormData, setLinkFormData] = useState<{ to_type: string; to_id: string }>({ to_type: '', to_id: '' });
  const [showVersionDrawer, setShowVersionDrawer] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<RiskItemVersion | null>(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [approvalData, setApprovalData] = useState<{ version_id: string; decision: 'approved' | 'rejected'; rationale: string }>({
    version_id: '',
    decision: 'approved',
    rationale: '',
  });
  const [showDemoModal, setShowDemoModal] = useState(false);
  const [demoLinkIds, setDemoLinkIds] = useState<{ design_input?: string; design_output?: string; capa?: string; change_control?: string }>({});
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [compareVersions, setCompareVersions] = useState<{ v1?: RiskItemVersion; v2?: RiskItemVersion }>({});
  const [approvedVersion, setApprovedVersion] = useState<RiskItemVersion | null>(null);
  const [showApprovalWarning, setShowApprovalWarning] = useState(false);
  const [aiEvents, setAiEvents] = useState<AIEvent[]>([]);
  const [currentAIEventId, setCurrentAIEventId] = useState<string | null>(null);
  const [showDesignHandoffModal, setShowDesignHandoffModal] = useState(false);
  const [selectedControlForHandoff, setSelectedControlForHandoff] = useState<RiskControl | null>(null);
  const [designHandoffType, setDesignHandoffType] = useState<'design_input' | 'design_output' | 'vv_test' | null>(null);
  const [designHandoffData, setDesignHandoffData] = useState<{ name?: string; description?: string; test_method?: string; acceptance_criteria?: string; design_output_id?: string }>({});
  const [showCAPAHandoffModal, setShowCAPAHandoffModal] = useState(false);
  const [capaHandoffData, setCapaHandoffData] = useState<{ title?: string; root_cause?: string; capa_plan?: string }>({});
  const [showChangeHandoffModal, setShowChangeHandoffModal] = useState(false);
  const [changeHandoffVersionId, setChangeHandoffVersionId] = useState<string | null>(null);
  const [recentHandoffs, setRecentHandoffs] = useState<Array<{
    id: string;
    type: 'design' | 'capa' | 'change';
    artifactType?: string;
    artifactId: string;
    linkId: string;
    message: string;
    timestamp: Date;
  }>>([]);
  const [vvModalOpen, setVVModalOpen] = useState(false);
  const [vvLoading, setVVLoading] = useState(false);
  const [vvError, setVVError] = useState<string | null>(null);
  const [vvData, setVVData] = useState<any>(null);

  const { addToast } = useToast();
  const finalProjectId = projectId || currentProject?.id || '';

  useEffect(() => {
    if (finalProjectId && riskItemId) {
      loadData();
    }
  }, [finalProjectId, riskItemId]);

  const loadData = async () => {
    if (!finalProjectId || !riskItemId) return;
    
    try {
      setLoading(true);
      const [item, vers, ctrls, lnks, events] = await Promise.all([
        getRiskItem(finalProjectId, riskItemId),
        listRiskVersions(finalProjectId, riskItemId),
        listRiskControls(finalProjectId, riskItemId),
        listRiskLinks(finalProjectId, riskItemId),
        getRiskItemAIEvents(finalProjectId, riskItemId).catch(() => []), // Fail gracefully
      ]);
      
      setRiskItem(item);
      setVersions(vers);
      setControls(ctrls);
      setLinks(lnks);
      setAiEvents(events);
      
      // Find approved version (simplified - in real app would check approvals table)
      const approved = vers.find(v => v.risk_acceptability === 'acceptable' && v.version_number === Math.max(...vers.map(vv => vv.version_number)));
      setApprovedVersion(approved || null);
      
      // Initialize current version data from latest version or risk item
      if (item.current_version) {
        setCurrentVersionData({
          hazard: item.current_version.hazard,
          hazardous_situation: item.current_version.hazardous_situation,
          harm: item.current_version.harm,
          failure_mode: item.current_version.failure_mode,
          severity: item.current_version.severity,
          probability_of_harm: item.current_version.probability_of_harm,
          occurrence: item.current_version.occurrence,
          detection: item.current_version.detection,
          inherent_safety: item.current_version.inherent_safety,
          protective_measures: item.current_version.protective_measures,
          information_for_safety: item.current_version.information_for_safety,
          residual_severity: item.current_version.residual_severity,
          residual_probability_of_harm: item.current_version.residual_probability_of_harm,
          residual_detection: item.current_version.residual_detection,
          benefit_risk_summary: item.current_version.benefit_risk_summary,
          overall_residual_risk_conclusion: item.current_version.overall_residual_risk_conclusion,
          risk_acceptability: item.current_version.risk_acceptability,
          risk_rationale: item.current_version.risk_rationale,
        });
      }
    } catch (error) {
      console.error('Error loading data:', error);
      alert('Failed to load risk item data');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveVersion = async () => {
    if (!finalProjectId || !riskItemId) return;
    
    // Check if editing after approval
    if (approvedVersion && !currentVersionData.risk_rationale && !currentVersionData.change_summary) {
      setShowApprovalWarning(true);
      return;
    }
    
    // Require rationale if post-approval edit
    if (approvedVersion && !currentVersionData.risk_rationale) {
      alert('Risk rationale is required when editing an approved version');
      return;
    }
    
    try {
      await updateRiskItem(finalProjectId, riskItemId, currentVersionData);
      addToast('Risk item updated (new version created)', 'success');
      loadData();
    } catch (error) {
      console.error('Error saving version:', error);
      addToast('Failed to save version', 'error');
    }
  };

  const handleDemoFlow = async () => {
    if (!finalProjectId || !riskItemId) return;
    
    try {
      // Create a sample control
      await createRiskControl(finalProjectId, riskItemId, {
        risk_item_id: riskItemId,
        project_id: finalProjectId,
        control_name: 'Sample Protective Control',
        control_description: 'Demo control created by wizard',
        control_type: 'protective',
        status: 'active',
      });
      
      // Create trace links (use placeholder IDs if not provided)
      const linkPromises = [];
      
      // Design Input
      linkPromises.push(createRiskLink(finalProjectId, riskItemId, {
        to_type: 'design_input',
        to_id: demoLinkIds.design_input || `demo-di-${Date.now()}`,
      }));
      
      // Design Output
      linkPromises.push(createRiskLink(finalProjectId, riskItemId, {
        to_type: 'design_output',
        to_id: demoLinkIds.design_output || `demo-do-${Date.now()}`,
      }));
      
      // CAPA
      linkPromises.push(createRiskLink(finalProjectId, riskItemId, {
        to_type: 'capa',
        to_id: demoLinkIds.capa || `demo-capa-${Date.now()}`,
      }));
      
      // Change Control
      if (demoLinkIds.change_control) {
        linkPromises.push(createRiskLink(finalProjectId, riskItemId, {
          to_type: 'change_control',
          to_id: demoLinkIds.change_control,
        }));
      }
      
      await Promise.all(linkPromises);
      
      setShowDemoModal(false);
      setDemoLinkIds({});
      
      // Switch to traceability tab and show toast
      setActiveTab('traceability');
      addToast('Demo links created! Check the Traceability tab.', 'success');
      
      // Refresh data
      loadData();
    } catch (error) {
      console.error('Error creating demo flow:', error);
      addToast('Failed to create demo flow', 'error');
    }
  };

  const handleCompareVersions = () => {
    if (!compareVersions.v1 || !compareVersions.v2) {
      alert('Please select two versions to compare');
      return;
    }
    setShowCompareModal(true);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    addToast('Copied to clipboard', 'success');
  };

  const handleDesignHandoff = async () => {
    if (!finalProjectId || !riskItemId || !selectedControlForHandoff || !designHandoffType) return;
    
    // Generate idempotency key
    const idempotencyKey = crypto.randomUUID();
    
    try {
      const result = await handoffControlToDesign(
        finalProjectId,
        riskItemId,
        selectedControlForHandoff.id,
        {
          target_type: designHandoffType,
          name: designHandoffData.name || selectedControlForHandoff.control_name,
          description: designHandoffData.description || selectedControlForHandoff.control_description || '',
          test_method: designHandoffData.test_method,
          acceptance_criteria: designHandoffData.acceptance_criteria,
          design_output_id: designHandoffData.design_output_id,
        },
        idempotencyKey
      );
      
      setShowDesignHandoffModal(false);
      setSelectedControlForHandoff(null);
      setDesignHandoffType(null);
      setDesignHandoffData({});
      
      // Add to recent handoffs
      const artifactType = designHandoffType === 'design_input' ? 'DI' : designHandoffType === 'design_output' ? 'DO' : 'V&V';
      const artifactId = result.created_artifact?.id?.slice(0, 8) || 'unknown';
      const handoffEntry = {
        id: crypto.randomUUID(),
        type: 'design' as const,
        artifactType: designHandoffType,
        artifactId: result.created_artifact.id,
        linkId: result.trace_link.id,
        message: `Created ${artifactType}-${artifactId} and linked to ${selectedControlForHandoff.control_name}`,
        timestamp: new Date(),
      };
      setRecentHandoffs(prev => [handoffEntry, ...prev].slice(0, 5));
      
      addToast(handoffEntry.message, 'success');
      setActiveTab('traceability');
      loadData();
    } catch (error) {
      console.error('Error creating design handoff:', error);
      addToast('Failed to create design artifact', 'error');
    }
  };

  const handleCAPAHandoff = async () => {
    if (!finalProjectId || !riskItemId) return;
    
    // Generate idempotency key
    const idempotencyKey = crypto.randomUUID();
    
    try {
      const result = await handoffRiskToCAPA(
        finalProjectId,
        riskItemId,
        capaHandoffData,
        idempotencyKey
      );
      
      setShowCAPAHandoffModal(false);
      setCapaHandoffData({});
      
      // Add to recent handoffs
      const capaId = result.created_artifact?.id?.slice(0, 8) || 'unknown';
      const handoffEntry = {
        id: crypto.randomUUID(),
        type: 'capa' as const,
        artifactType: 'capa',
        artifactId: result.created_artifact.id,
        linkId: result.trace_link.id,
        message: `Created CAPA-${capaId} from ${riskItem?.title || 'Risk'}`,
        timestamp: new Date(),
      };
      setRecentHandoffs(prev => [handoffEntry, ...prev].slice(0, 5));
      
      addToast(handoffEntry.message, 'success');
      setActiveTab('traceability');
      loadData();
      
      // Navigate to CAPA if route exists
      // navigate(`/projects/${finalProjectId}/capa/${result.created_artifact.id}`);
    } catch (error) {
      console.error('Error creating CAPA handoff:', error);
      addToast('Failed to create CAPA', 'error');
    }
  };

  const handleChangeHandoff = async () => {
    if (!finalProjectId || !riskItemId) return;
    
    // Generate idempotency key
    const idempotencyKey = crypto.randomUUID();
    
    try {
      const result = await handoffRiskVersionToChange(
        finalProjectId,
        riskItemId,
        {
          version_id: changeHandoffVersionId || undefined,
        },
        idempotencyKey
      );
      
      setShowChangeHandoffModal(false);
      setChangeHandoffVersionId(null);
      
      // Add to recent handoffs
      const changeId = result.created_artifact?.id?.slice(0, 8) || 'unknown';
      const versionNum = versions.find(v => v.id === changeHandoffVersionId)?.version_number || 'current';
      const handoffEntry = {
        id: crypto.randomUUID(),
        type: 'change' as const,
        artifactType: 'change_control',
        artifactId: result.created_artifact.id,
        linkId: result.trace_link.id,
        message: `Created Change-${changeId} from v${versionNum}`,
        timestamp: new Date(),
      };
      setRecentHandoffs(prev => [handoffEntry, ...prev].slice(0, 5));
      
      addToast(handoffEntry.message, 'success');
      setActiveTab('traceability');
      loadData();
    } catch (error) {
      console.error('Error creating change control handoff:', error);
      addToast('Failed to create Change Control', 'error');
    }
  };

  const handleCreateControl = async () => {
    if (!finalProjectId || !riskItemId) return;
    
    try {
      await createRiskControl(finalProjectId, riskItemId, {
        ...controlFormData,
        risk_item_id: riskItemId,
        project_id: finalProjectId,
      } as RiskControlCreate);
      
      setShowControlModal(false);
      setControlFormData({});
      loadData();
    } catch (error) {
      console.error('Error creating control:', error);
      alert('Failed to create control');
    }
  };

  const handleUpdateControl = async () => {
    if (!finalProjectId || !riskItemId || !selectedControl) return;
    
    try {
      await patchRiskControl(finalProjectId, riskItemId, selectedControl.id, controlFormData as RiskControlUpdate);
      setShowControlModal(false);
      setSelectedControl(null);
      setControlFormData({});
      loadData();
    } catch (error) {
      console.error('Error updating control:', error);
      alert('Failed to update control');
    }
  };

  const handleDeleteControl = async (controlId: string) => {
    if (!finalProjectId || !riskItemId) return;
    if (!confirm('Are you sure you want to delete this control?')) return;
    
    try {
      await deleteRiskControl(finalProjectId, riskItemId, controlId);
      loadData();
    } catch (error) {
      console.error('Error deleting control:', error);
      alert('Failed to delete control');
    }
  };

  const handleCreateLink = async () => {
    if (!finalProjectId || !riskItemId || !linkFormData.to_type || !linkFormData.to_id) {
      alert('Please select link type and provide ID');
      return;
    }
    
    try {
      await createRiskLink(finalProjectId, riskItemId, linkFormData);
      setShowLinkModal(false);
      setLinkFormData({ to_type: '', to_id: '' });
      loadData();
    } catch (error) {
      console.error('Error creating link:', error);
      alert('Failed to create link');
    }
  };

  const handleApprove = async () => {
    if (!finalProjectId || !riskItemId || !approvalData.rationale) {
      alert('Please provide rationale');
      return;
    }
    
    try {
      await approveRiskVersion(finalProjectId, riskItemId, approvalData);
      alert('Version approved');
      setShowApproveModal(false);
      setApprovalData({ version_id: '', decision: 'approved', rationale: '' });
      loadData();
    } catch (error) {
      console.error('Error approving version:', error);
      alert('Failed to approve version');
    }
  };

  const viewVersion = async (versionId: string) => {
    if (!finalProjectId || !riskItemId) return;
    
    try {
      const version = await getRiskVersion(finalProjectId, riskItemId, versionId);
      setSelectedVersion(version);
      setShowVersionDrawer(true);
    } catch (error) {
      console.error('Error loading version:', error);
      alert('Failed to load version');
    }
  };

  const openGenerateVV = async () => {
    if (!riskItem) return;
    const v = riskItem.current_version;
    setVVModalOpen(true);
    setVVError(null);
    setVVData(null);
    setVVLoading(true);
    const payload = {
      component: riskItem.title || 'Risk item',
      failure_mode: v?.failure_mode || riskItem.description || '',
      effect: v?.harm || v?.hazardous_situation || riskItem.description || '',
      cause: v?.sequence_of_events || riskItem.description || '',
      severity: v?.severity ?? riskItem.severity ?? 1,
      probability: v?.probability ?? v?.occurrence ?? riskItem.probability ?? 1,
      detection: v?.detection ?? 1,
      mitigation: v?.control_measures_summary || v?.protective_measures || riskItem.mitigation_strategy || riskItem.control_measures || '',
      residual_severity: v?.residual_severity ?? undefined,
      residual_occurrence: v?.residual_probability_of_harm ?? v?.residual_occurrence ?? undefined,
      residual_detection: v?.residual_detection ?? undefined,
      residual_rpn: v?.residual_risk_score ?? undefined,
    };
    try {
      const data = await generateVVFromRisk(payload);
      setVVData(data);
    } catch (e: any) {
      const detail = e?.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : e?.message || 'Failed to generate V&V';
      setVVError(msg);
    } finally {
      setVVLoading(false);
    }
  };

  const closeVVModal = () => {
    setVVModalOpen(false);
    setVVData(null);
    setVVError(null);
  };

  if (loading) {
    return (
      <div className="p-6">
        <Card>
          <div className="text-center py-8 text-text-secondary">Loading...</div>
        </Card>
      </div>
    );
  }

  if (!riskItem) {
    return (
      <div className="p-6">
        <Card>
          <div className="text-center py-8 text-text-secondary">Risk item not found</div>
        </Card>
      </div>
    );
  }

  const currentVersion = riskItem.current_version;
  const versionInfo = currentVersion
    ? `v${currentVersion.version_number} (created by ${currentVersion.changed_by || 'system'} on ${new Date(currentVersion.created_at).toLocaleDateString()})`
    : 'No version yet';

  return (
    <div className="p-6">
      <PageHeader
        title={riskItem.title}
        description={`Current Version: ${versionInfo}${approvedVersion ? ` | Approved: v${approvedVersion.version_number}` : ''}`}
        actions={
          <>
            <Button
              variant="ghost"
              onClick={openGenerateVV}
              title="Generate V&V test logic from this risk record"
            >
              🔬 Generate V&V
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                if (!riskItem) return;
                const evidenceData: RiskEvidenceData = {
                  riskItem,
                  versions,
                  approvals: [], // TODO: Fetch from approvals API
                  aiEvents,
                  traceLinks: links,
                };
                const riskKey = riskItem.title || riskItem.id.slice(0, 8);
                exportRiskEvidenceHTML(evidenceData, `risk-${riskKey}`);
              }}
              title="Export Evidence Pack (HTML)"
            >
              📄 Export Evidence
            </Button>
            <Button
              variant="ghost"
              onClick={() => setShowDemoModal(true)}
            >
              🎯 Demo Flow
            </Button>
            <Button
              variant="secondary"
              onClick={() => {
                const basePath = projectId ? `/projects/${finalProjectId}` : '';
                navigate(`${basePath}/risk-items`);
              }}
            >
              Back to List
            </Button>
          </>
        }
      />

      {/* Approval Banner */}
      {approvedVersion && (
        <Card className="mb-6 bg-primary/10 border-primary/30">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-semibold text-primary mb-1">
                Approved: v{approvedVersion.version_number} on {new Date(approvedVersion.created_at).toLocaleDateString()}
              </div>
              <div className="text-sm text-text-secondary">
                {approvedVersion.risk_rationale || 'Approved version'}
              </div>
            </div>
            <Badge variant="success">Approved</Badge>
          </div>
        </Card>
      )}

      {/* Post-approval draft warning */}
      {approvedVersion && currentVersionData.risk_rationale && (
        <Card className="mb-6 bg-amber-500/10 border-amber-500/30">
          <div className="flex items-center gap-2">
            <span className="text-amber-600">⚠️</span>
            <span className="text-sm font-medium text-amber-600">
              Draft (post-approval change) - Requires re-approval
            </span>
          </div>
        </Card>
      )}

      {/* Downstream Links Panel */}
      {finalProjectId && riskItemId && links.from.length > 0 && (
        <div className="mb-6">
          <DownstreamLinksPanel
            projectId={finalProjectId}
            links={links.from}
            onNavigate={(route) => navigate(route)}
            title="Downstream Artifacts (Linked)"
          />
        </div>
      )}

      {/* Recent Handoffs Panel */}
      {recentHandoffs.length > 0 && (
        <Card className="mb-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-text-primary">Recent Handoffs</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setRecentHandoffs([])}
            >
              Clear
            </Button>
          </div>
          <div className="space-y-2">
            {recentHandoffs.map((handoff) => {
              // Build route to downstream artifact
              let route: string | null = null;
              
              if (handoff.type === 'design' && handoff.artifactType) {
                if (handoff.artifactType === 'design_input') {
                  route = `/projects/${finalProjectId}/design-inputs/${handoff.artifactId}`;
                } else if (handoff.artifactType === 'design_output') {
                  route = `/projects/${finalProjectId}/design-outputs/${handoff.artifactId}`;
                } else if (handoff.artifactType === 'vv_test') {
                  route = `/projects/${finalProjectId}/vv-tests/${handoff.artifactId}`;
                }
              } else if (handoff.type === 'capa') {
                route = `/projects/${finalProjectId}/capas/${handoff.artifactId}`;
              } else if (handoff.type === 'change') {
                route = `/projects/${finalProjectId}/change-controls/${handoff.artifactId}`;
              }

              return (
                <div
                  key={handoff.id}
                  className={`flex items-center justify-between p-2 bg-surface-secondary rounded-lg text-sm ${
                    route ? 'cursor-pointer hover:bg-surface-hover transition-colors' : ''
                  }`}
                  onClick={() => {
                    if (route) {
                      navigate(route);
                    }
                  }}
                >
                  <div className="flex items-center gap-2">
                    <Badge variant={
                      handoff.type === 'design' ? 'primary' :
                      handoff.type === 'capa' ? 'warning' : 'info'
                    }>
                      {handoff.type.toUpperCase()}
                    </Badge>
                    <span className="text-text-primary">{handoff.message}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-text-secondary text-xs">
                      {handoff.timestamp.toLocaleTimeString()}
                    </span>
                    {route && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(route);
                        }}
                      >
                        View →
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Tabs */}
      <div className="border-b border-border mb-6">
        <div className="flex gap-4">
          {(['current', 'controls', 'traceability', 'versions', 'approval', 'graph'] as TabType[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`
                px-4 py-2 font-medium transition-smooth border-b-2
                ${activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-text-secondary hover:text-text-primary'
                }
              `}
            >
              {tab === 'graph' ? 'Connected Graph' : tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Current Version Tab */}
      {activeTab === 'current' && (
        <div className="space-y-6">
          {/* ISO 14971 Chain */}
          <Card>
            <h3 className="text-h3 font-semibold mb-4">ISO 14971 Chain</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Textarea
                label="Hazard"
                value={currentVersionData.hazard || ''}
                onChange={(e) => {
                  if (approvedVersion) {
                    // Show warning if editing key fields after approval
                    const keyFields = ['hazard', 'harm', 'severity', 'probability_of_harm'];
                    if (keyFields.includes('hazard') && e.target.value !== currentVersionData.hazard) {
                      if (!currentVersionData.risk_rationale) {
                        setShowApprovalWarning(true);
                      }
                    }
                  }
                  setCurrentVersionData({ ...currentVersionData, hazard: e.target.value });
                }}
                rows={3}
              />
              <Textarea
                label="Hazardous Situation"
                value={currentVersionData.hazardous_situation || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, hazardous_situation: e.target.value })}
                rows={3}
              />
              <Textarea
                label="Harm"
                value={currentVersionData.harm || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, harm: e.target.value })}
                rows={3}
              />
              <Input
                label="Failure Mode"
                value={currentVersionData.failure_mode || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, failure_mode: e.target.value })}
              />
            </div>
          </Card>

          {/* Risk Estimation */}
          <Card>
            <h3 className="text-h3 font-semibold mb-4">Risk Estimation</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Input
                label="Severity (1-10)"
                type="number"
                min="1"
                max="10"
                value={currentVersionData.severity || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, severity: parseInt(e.target.value) || undefined })}
              />
              <Input
                label="Probability of Harm (1-10)"
                type="number"
                min="1"
                max="10"
                value={currentVersionData.probability_of_harm || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, probability_of_harm: parseInt(e.target.value) || undefined })}
              />
              <Input
                label="Occurrence (1-10)"
                type="number"
                min="1"
                max="10"
                value={currentVersionData.occurrence || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, occurrence: parseInt(e.target.value) || undefined })}
              />
              <Input
                label="Detection (1-10)"
                type="number"
                min="1"
                max="10"
                value={currentVersionData.detection || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, detection: parseInt(e.target.value) || undefined })}
              />
            </div>
            <div className="mt-4">
              <Badge variant="info">
                Risk Score: {currentVersion?.risk_score || 'N/A'} ({currentVersion?.risk_level || 'N/A'})
              </Badge>
            </div>
          </Card>

          {/* Acceptability & Rationale */}
          <Card>
            <h3 className="text-h3 font-semibold mb-4">Acceptability & Rationale</h3>
            <div className="space-y-4">
              <select
                className="w-full px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary"
                value={currentVersionData.risk_acceptability || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, risk_acceptability: e.target.value })}
              >
                <option value="">Select...</option>
                <option value="acceptable">Acceptable</option>
                <option value="unacceptable">Unacceptable</option>
                <option value="needs_benefit_risk">Needs Benefit-Risk</option>
              </select>
              <Textarea
                label="Risk Rationale"
                value={currentVersionData.risk_rationale || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, risk_rationale: e.target.value })}
                rows={4}
              />
            </div>
          </Card>

          {/* Residual Risk */}
          <Card>
            <h3 className="text-h3 font-semibold mb-4">Residual Risk</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <Input
                label="Residual Severity"
                type="number"
                min="1"
                max="10"
                value={currentVersionData.residual_severity || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, residual_severity: parseInt(e.target.value) || undefined })}
              />
              <Input
                label="Residual Probability of Harm"
                type="number"
                min="1"
                max="10"
                value={currentVersionData.residual_probability_of_harm || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, residual_probability_of_harm: parseInt(e.target.value) || undefined })}
              />
              <Input
                label="Residual Detection"
                type="number"
                min="1"
                max="10"
                value={currentVersionData.residual_detection || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, residual_detection: parseInt(e.target.value) || undefined })}
              />
              <div className="flex items-end">
                <Badge variant="info">
                  Residual Score: {currentVersion?.residual_risk_score || 'N/A'}
                </Badge>
              </div>
            </div>
            <div className="space-y-4">
              <Textarea
                label="Benefit-Risk Summary"
                value={currentVersionData.benefit_risk_summary || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, benefit_risk_summary: e.target.value })}
                rows={3}
              />
              <Textarea
                label="Overall Residual Risk Conclusion"
                value={currentVersionData.overall_residual_risk_conclusion || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, overall_residual_risk_conclusion: e.target.value })}
                rows={3}
              />
            </div>
          </Card>

          {/* Control Measures */}
          <Card>
            <h3 className="text-h3 font-semibold mb-4">Control Measures</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Textarea
                label="Inherent Safety"
                value={currentVersionData.inherent_safety || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, inherent_safety: e.target.value })}
                rows={4}
              />
              <Textarea
                label="Protective Measures"
                value={currentVersionData.protective_measures || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, protective_measures: e.target.value })}
                rows={4}
              />
              <Textarea
                label="Information for Safety"
                value={currentVersionData.information_for_safety || ''}
                onChange={(e) => setCurrentVersionData({ ...currentVersionData, information_for_safety: e.target.value })}
                rows={4}
              />
            </div>
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Button onClick={handleSaveVersion}>Save New Version</Button>
            <Button variant="secondary" onClick={() => setShowCAPAHandoffModal(true)}>
              Create CAPA from this Risk
            </Button>
            <Button variant="secondary" onClick={loadData}>Reset</Button>
          </div>

          {/* AI Suggestions Panel */}
          <Card className="mt-6">
            <h3 className="text-h3 font-semibold mb-4">AI Suggestions</h3>
            <div className="space-y-4">
              <Button
                variant="secondary"
                onClick={async () => {
                  try {
                    const { suggestions, ai_event_id } = await getAIRiskSuggestions(
                      finalProjectId,
                      riskItemId,
                      {
                        hazard: currentVersionData.hazard,
                        hazardous_situation: currentVersionData.hazardous_situation,
                        harm: currentVersionData.harm,
                      }
                    );
                    
                    // Apply suggestions to form
                    setCurrentVersionData({
                      ...currentVersionData,
                      severity: suggestions.severity,
                      probability_of_harm: suggestions.probability_of_harm,
                      detection: suggestions.detection,
                      residual_severity: suggestions.residual_severity,
                      residual_probability_of_harm: suggestions.residual_probability_of_harm,
                      residual_detection: suggestions.residual_detection,
                    });
                    
                    setCurrentAIEventId(ai_event_id);
                    addToast('AI suggestions applied. Review and save.', 'success');
                    loadData(); // Refresh to show new AI event
                  } catch (error) {
                    console.error('Error getting AI suggestions:', error);
                    addToast('Failed to get AI suggestions', 'error');
                  }
                }}
              >
                Get AI Risk Assessment Suggestions
              </Button>
              
              {/* AI Event History */}
              {aiEvents.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-semibold mb-3">AI Event History</h4>
                  <div className="space-y-2">
                    {aiEvents.map((event) => (
                      <div key={event.id} className="p-3 bg-surface-secondary rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="text-sm font-medium">
                              {event.prompt_name} - {new Date(event.created_at).toLocaleString()}
                            </div>
                            {event.disposition && (
                              <Badge variant={event.disposition === 'accepted' ? 'success' : 'default'} className="mt-1">
                                {event.disposition}
                              </Badge>
                            )}
                          </div>
                          {event.disposition === 'pending' && event.id === currentAIEventId && (
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="primary"
                                onClick={async () => {
                                  try {
                                    await updateAIEventDisposition(event.id, {
                                      disposition: 'accepted',
                                      disposition_notes: 'Accepted as-is'
                                    });
                                    addToast('AI suggestion accepted', 'success');
                                    loadData();
                                  } catch (error) {
                                    addToast('Failed to update disposition', 'error');
                                  }
                                }}
                              >
                                Accept
                              </Button>
                              <Button
                                size="sm"
                                variant="secondary"
                                onClick={async () => {
                                  try {
                                    await updateAIEventDisposition(event.id, {
                                      disposition: 'edited',
                                      disposition_notes: 'Edited before accepting'
                                    });
                                    addToast('Marked as edited', 'success');
                                    loadData();
                                  } catch (error) {
                                    addToast('Failed to update disposition', 'error');
                                  }
                                }}
                              >
                                Edit
                              </Button>
                              <Button
                                size="sm"
                                variant="danger"
                                onClick={async () => {
                                  try {
                                    await updateAIEventDisposition(event.id, {
                                      disposition: 'rejected',
                                      disposition_notes: 'Rejected'
                                    });
                                    addToast('AI suggestion rejected', 'success');
                                    loadData();
                                  } catch (error) {
                                    addToast('Failed to update disposition', 'error');
                                  }
                                }}
                              >
                                Reject
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Controls Tab */}
      {activeTab === 'controls' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-h3 font-semibold">Risk Controls</h3>
            <Button onClick={() => { setSelectedControl(null); setControlFormData({}); setShowControlModal(true); }}>
              Add Control
            </Button>
          </div>
          
          <DataTable
            data={controls}
            columns={[
              {
                key: 'control_name',
                header: 'Name',
                render: (c: RiskControl) => <div className="font-medium">{c.control_name}</div>,
              },
              {
                key: 'control_type',
                header: 'Type',
                render: (c: RiskControl) => (
                  <Badge variant={c.control_type === 'protective' ? 'info' : 'default'}>
                    {c.control_type}
                  </Badge>
                ),
              },
              {
                key: 'status',
                header: 'Status',
                render: (c: RiskControl) => (
                  <Badge variant={c.status === 'active' ? 'success' : 'default'}>
                    {c.status}
                  </Badge>
                ),
              },
              {
                key: 'actions',
                header: 'Actions',
                render: (c: RiskControl) => (
                  <div className="flex gap-2 flex-wrap">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSelectedControl(c);
                        setControlFormData(c);
                        setShowControlModal(true);
                      }}
                    >
                      Edit
                    </Button>
                    <div className="relative group">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setSelectedControlForHandoff(c);
                          setShowDesignHandoffModal(true);
                        }}
                      >
                        Create From...
                      </Button>
                    </div>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDeleteControl(c.id)}
                    >
                      Delete
                    </Button>
                  </div>
                ),
              },
            ]}
            emptyMessage="No controls yet. Add one to get started."
          />
        </div>
      )}

      {/* Traceability Tab */}
      {activeTab === 'traceability' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-h3 font-semibold">Traceability Links</h3>
            <Button onClick={() => setShowLinkModal(true)}>Create Link</Button>
          </div>

          {/* Filter and Search */}
          <Card>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                placeholder="Search links..."
                onChange={(e) => {
                  // Filter logic can be added here
                }}
              />
              <select className="px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary">
                <option value="">All Types</option>
                <option value="design_input">Design Input</option>
                <option value="design_output">Design Output</option>
                <option value="vv_test">V&V Test</option>
                <option value="capa">CAPA</option>
                <option value="change_control">Change Control</option>
              </select>
            </div>
          </Card>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <h4 className="font-semibold mb-4">Links From This Risk Item</h4>
              <div className="space-y-2">
                {links.from.length === 0 ? (
                  <p className="text-text-secondary">No outgoing links</p>
                ) : (
                  (() => {
                    // Group by type
                    const grouped: Record<string, TraceLink[]> = {};
                    links.from.forEach(link => {
                      if (!grouped[link.to_type]) grouped[link.to_type] = [];
                      grouped[link.to_type].push(link);
                    });

                    return Object.entries(grouped).map(([type, typeLinks]) => (
                      <div key={type} className="mb-4">
                        <h5 className="text-sm font-semibold text-text-secondary mb-2 uppercase">
                          {type.replace(/_/g, ' ')}
                        </h5>
                        {typeLinks.map((link) => {
                          const route = getArtifactRoute(link.to_type as any, link.to_id, finalProjectId);
                          
                          return (
                            <div key={link.id} className="p-3 bg-surface-secondary rounded-lg mb-2">
                              <div className="flex justify-between items-center">
                                <div>
                                  {route ? (
                                    <button
                                      onClick={() => navigate(route)}
                                      className="text-primary hover:underline font-medium"
                                    >
                                      {link.to_type.replace(/_/g, ' ')}: {link.to_id.slice(0, 8)}...
                                    </button>
                                  ) : (
                                    <span className="font-medium text-text-secondary">
                                      {link.to_type.replace(/_/g, ' ')}: {link.to_id.slice(0, 8)}...
                                    </span>
                                  )}
                                </div>
                                <div className="flex gap-2">
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => copyToClipboard(link.to_id)}
                                  >
                                    Copy ID
                                  </Button>
                                </div>
                              </div>
                              <p className="text-xs text-text-secondary mt-1">
                                Created: {new Date(link.created_at).toLocaleDateString()}
                              </p>
                            </div>
                          );
                        })}
                      </div>
                    ));
                  })()
                )}
              </div>
            </Card>
            
            <Card>
              <h4 className="font-semibold mb-4">Links To This Risk Item</h4>
              <div className="space-y-2">
                {links.to.length === 0 ? (
                  <p className="text-text-secondary">No incoming links</p>
                ) : (
                  (() => {
                    const grouped: Record<string, TraceLink[]> = {};
                    links.to.forEach(link => {
                      if (!grouped[link.from_type]) grouped[link.from_type] = [];
                      grouped[link.from_type].push(link);
                    });

                    return Object.entries(grouped).map(([type, typeLinks]) => (
                      <div key={type} className="mb-4">
                        <h5 className="text-sm font-semibold text-text-secondary mb-2 uppercase">
                          {type.replace(/_/g, ' ')}
                        </h5>
                        {typeLinks.map((link) => (
                          <div key={link.id} className="p-3 bg-surface-secondary rounded-lg mb-2">
                            <div className="flex justify-between items-center">
                              <span className="font-medium">{link.from_type.replace(/_/g, ' ')}:</span>
                              <div className="flex gap-2">
                                <Badge>{link.from_id.substring(0, 8)}...</Badge>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => copyToClipboard(link.from_id)}
                                >
                                  Copy
                                </Button>
                              </div>
                            </div>
                            <p className="text-xs text-text-secondary mt-1">
                              Created: {new Date(link.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        ))}
                      </div>
                    ));
                  })()
                )}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Versions Tab */}
      {activeTab === 'versions' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-h3 font-semibold">Version History</h3>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={handleCompareVersions}
                disabled={!compareVersions.v1 || !compareVersions.v2}
              >
                Compare Selected
              </Button>
              {compareVersions.v2 && (
                <>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      // Copy newer version to current form
                      const newer = compareVersions.v2!;
                      setCurrentVersionData({
                        hazard: newer.hazard,
                        hazardous_situation: newer.hazardous_situation,
                        harm: newer.harm,
                        failure_mode: newer.failure_mode,
                        severity: newer.severity,
                        probability_of_harm: newer.probability_of_harm,
                        occurrence: newer.occurrence,
                        detection: newer.detection,
                        inherent_safety: newer.inherent_safety,
                        protective_measures: newer.protective_measures,
                        information_for_safety: newer.information_for_safety,
                        residual_severity: newer.residual_severity,
                        residual_probability_of_harm: newer.residual_probability_of_harm,
                        residual_detection: newer.residual_detection,
                        benefit_risk_summary: newer.benefit_risk_summary,
                        overall_residual_risk_conclusion: newer.overall_residual_risk_conclusion,
                        risk_acceptability: newer.risk_acceptability,
                        risk_rationale: newer.risk_rationale,
                      });
                      setActiveTab('current');
                      addToast('Version copied to form. Review and save to create new version.', 'info');
                    }}
                  >
                    Create New Version from Selected
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setChangeHandoffVersionId(compareVersions.v2!.id);
                      setShowChangeHandoffModal(true);
                    }}
                  >
                    Create Change Request from Version
                  </Button>
                </>
              )}
            </div>
          </div>
          <DataTable
            data={versions}
            columns={[
              {
                key: 'select',
                header: '',
                render: (v: RiskItemVersion) => (
                  <input
                    type="checkbox"
                    checked={compareVersions.v1?.id === v.id || compareVersions.v2?.id === v.id}
                    onChange={(e) => {
                      if (e.target.checked) {
                        if (!compareVersions.v1) {
                          setCompareVersions({ ...compareVersions, v1: v });
                        } else if (!compareVersions.v2) {
                          setCompareVersions({ ...compareVersions, v2: v });
                        }
                      } else {
                        if (compareVersions.v1?.id === v.id) {
                          setCompareVersions({ ...compareVersions, v1: undefined });
                        } else if (compareVersions.v2?.id === v.id) {
                          setCompareVersions({ ...compareVersions, v2: undefined });
                        }
                      }
                    }}
                  />
                ),
              },
              {
                key: 'version_number',
                header: 'Version',
                render: (v: RiskItemVersion) => (
                  <div className="font-medium">
                    v{v.version_number}
                    {approvedVersion?.id === v.id && (
                      <Badge variant="success" className="ml-2">Approved</Badge>
                    )}
                  </div>
                ),
              },
              {
                key: 'created_at',
                header: 'Created',
                render: (v: RiskItemVersion) => new Date(v.created_at).toLocaleString(),
              },
              {
                key: 'changed_by',
                header: 'Created By',
                render: (v: RiskItemVersion) => v.changed_by || 'system',
              },
              {
                key: 'risk_score',
                header: 'Risk Score',
                render: (v: RiskItemVersion) => (
                  <Badge variant={v.risk_score && v.risk_score >= 400 ? 'danger' : 'default'}>
                    {v.risk_score || 'N/A'}
                  </Badge>
                ),
              },
              {
                key: 'acceptability',
                header: 'Acceptability',
                render: (v: RiskItemVersion) => v.risk_acceptability || '-',
              },
              {
                key: 'actions',
                header: 'Actions',
                render: (v: RiskItemVersion) => (
                  <div className="flex gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => viewVersion(v.id)}
                    >
                      View
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setChangeHandoffVersionId(v.id);
                        setShowChangeHandoffModal(true);
                      }}
                    >
                      Create Change
                    </Button>
                  </div>
                ),
              },
            ]}
            emptyMessage="No versions yet"
          />
        </div>
      )}

      {/* Connected Graph Tab */}
      {activeTab === 'graph' && riskItem && (
        <ConnectedGraphView
          riskItem={riskItem}
          controls={controls}
          traceLinks={links}
          projectId={finalProjectId}
          onNavigate={(route) => navigate(route)}
        />
      )}

      {/* Approval Tab */}
      {activeTab === 'approval' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-h3 font-semibold">Approval / Governance</h3>
            <Button onClick={() => setShowApproveModal(true)}>Approve Version</Button>
          </div>
          
          <Card>
            <h4 className="font-semibold mb-4">Current Approval State</h4>
            <p className="text-text-secondary">
              {currentVersion?.risk_acceptability || 'Not yet approved'}
            </p>
          </Card>
        </div>
      )}

      {/* Control Modal */}
      <Modal
        isOpen={showControlModal}
        onClose={() => {
          setShowControlModal(false);
          setSelectedControl(null);
          setControlFormData({});
        }}
        title={selectedControl ? 'Edit Control' : 'Add Control'}
        footer={
          <>
            <Button
              variant="ghost"
              onClick={() => {
                setShowControlModal(false);
                setSelectedControl(null);
                setControlFormData({});
              }}
            >
              Cancel
            </Button>
            <Button onClick={selectedControl ? handleUpdateControl : handleCreateControl}>
              {selectedControl ? 'Update' : 'Create'}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Control Name *"
            value={controlFormData.control_name || ''}
            onChange={(e) => setControlFormData({ ...controlFormData, control_name: e.target.value })}
          />
          <select
            className="w-full px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary"
            value={controlFormData.control_type || ''}
            onChange={(e) => setControlFormData({ ...controlFormData, control_type: e.target.value as any })}
          >
            <option value="">Select Type</option>
            <option value="inherent_safety">Inherent Safety</option>
            <option value="protective">Protective</option>
            <option value="information">Information</option>
          </select>
          <Textarea
            label="Description"
            value={controlFormData.control_description || ''}
            onChange={(e) => setControlFormData({ ...controlFormData, control_description: e.target.value })}
            rows={3}
          />
          <select
            className="w-full px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary"
            value={controlFormData.status || 'proposed'}
            onChange={(e) => setControlFormData({ ...controlFormData, status: e.target.value as any })}
          >
            <option value="proposed">Proposed</option>
            <option value="active">Active</option>
            <option value="retired">Retired</option>
          </select>
        </div>
      </Modal>

      {/* Link Modal */}
      <Modal
        isOpen={showLinkModal}
        onClose={() => setShowLinkModal(false)}
        title="Create Trace Link"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowLinkModal(false)}>Cancel</Button>
            <Button onClick={handleCreateLink}>Create</Button>
          </>
        }
      >
        <div className="space-y-4">
          <select
            className="w-full px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary"
            value={linkFormData.to_type}
            onChange={(e) => setLinkFormData({ ...linkFormData, to_type: e.target.value })}
          >
            <option value="">Select Link Type</option>
            <option value="design_input">Design Input</option>
            <option value="design_output">Design Output</option>
            <option value="vv_test">V&V Test</option>
            <option value="capa">CAPA</option>
            <option value="change_control">Change Control</option>
            <option value="fmea_row">FMEA Row</option>
          </select>
          <Input
            label="Target ID *"
            value={linkFormData.to_id}
            onChange={(e) => setLinkFormData({ ...linkFormData, to_id: e.target.value })}
            placeholder="Enter artifact ID"
          />
        </div>
      </Modal>

      {/* Version Drawer */}
      <Drawer
        isOpen={showVersionDrawer}
        onClose={() => {
          setShowVersionDrawer(false);
          setSelectedVersion(null);
        }}
        title={selectedVersion ? `Version ${selectedVersion.version_number}` : ''}
        width="600px"
      >
        {selectedVersion && (
          <div className="space-y-4">
            <div>
              <strong>Hazard:</strong>
              <p className="mt-1 text-text-secondary">{selectedVersion.hazard || '-'}</p>
            </div>
            <div>
              <strong>Risk Score:</strong>
              <Badge variant="info" className="ml-2">
                {selectedVersion.risk_score || 'N/A'} ({selectedVersion.risk_level || 'N/A'})
              </Badge>
            </div>
            <div>
              <strong>Acceptability:</strong>
              <p className="mt-1 text-text-secondary">{selectedVersion.risk_acceptability || '-'}</p>
            </div>
            <div>
              <strong>Rationale:</strong>
              <p className="mt-1 text-text-secondary">{selectedVersion.risk_rationale || '-'}</p>
            </div>
            <div>
              <strong>Created:</strong>
              <p className="mt-1 text-text-secondary">{new Date(selectedVersion.created_at).toLocaleString()}</p>
            </div>
          </div>
        )}
      </Drawer>

      {/* Approve Modal */}
      <Modal
        isOpen={showApproveModal}
        onClose={() => setShowApproveModal(false)}
        title="Approve Version"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowApproveModal(false)}>Cancel</Button>
            <Button onClick={handleApprove}>Approve</Button>
          </>
        }
      >
        <div className="space-y-4">
          <select
            className="w-full px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary"
            value={approvalData.version_id}
            onChange={(e) => setApprovalData({ ...approvalData, version_id: e.target.value })}
          >
            <option value="">Select Version</option>
            {versions.map((v) => (
              <option key={v.id} value={v.id}>
                v{v.version_number} - {new Date(v.created_at).toLocaleDateString()}
              </option>
            ))}
          </select>
          <select
            className="w-full px-4 py-2.5 bg-surface-secondary border border-border rounded-lg text-text-primary"
            value={approvalData.decision}
            onChange={(e) => setApprovalData({ ...approvalData, decision: e.target.value as any })}
          >
            <option value="approved">Approve</option>
            <option value="rejected">Reject</option>
          </select>
          <Textarea
            label="Rationale *"
            value={approvalData.rationale}
            onChange={(e) => setApprovalData({ ...approvalData, rationale: e.target.value })}
            rows={4}
            placeholder="Provide rationale for approval/rejection"
          />
        </div>
      </Modal>

      {/* Demo Flow Modal */}
      <Modal
        isOpen={showDemoModal}
        onClose={() => {
          setShowDemoModal(false);
          setDemoLinkIds({});
        }}
        title="Demo Flow - Connected System"
        size="md"
        footer={
          <>
            <Button variant="ghost" onClick={() => {
              setShowDemoModal(false);
              setDemoLinkIds({});
            }}>
              Cancel
            </Button>
            <Button onClick={handleDemoFlow}>
              Create Demo Links
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-text-secondary mb-4">
            This will create a sample control and trace links. Optionally enter artifact IDs, or leave blank to use placeholders.
          </p>
          
          <div className="space-y-3">
            <Input
              label="Design Input ID (optional)"
              value={demoLinkIds.design_input || ''}
              onChange={(e) => setDemoLinkIds({ ...demoLinkIds, design_input: e.target.value })}
              placeholder="Leave blank for placeholder"
            />
            <Input
              label="Design Output ID (optional)"
              value={demoLinkIds.design_output || ''}
              onChange={(e) => setDemoLinkIds({ ...demoLinkIds, design_output: e.target.value })}
              placeholder="Leave blank for placeholder"
            />
            <Input
              label="CAPA ID (optional)"
              value={demoLinkIds.capa || ''}
              onChange={(e) => setDemoLinkIds({ ...demoLinkIds, capa: e.target.value })}
              placeholder="Leave blank for placeholder"
            />
            <Input
              label="Change Control ID (optional)"
              value={demoLinkIds.change_control || ''}
              onChange={(e) => setDemoLinkIds({ ...demoLinkIds, change_control: e.target.value })}
              placeholder="Leave blank for placeholder"
            />
          </div>
        </div>
      </Modal>

      {/* Version Compare Modal */}
      <Modal
        isOpen={showCompareModal}
        onClose={() => {
          setShowCompareModal(false);
          setCompareVersions({});
        }}
        title={`Compare v${compareVersions.v1?.version_number} vs v${compareVersions.v2?.version_number}`}
        size="xl"
        footer={
          <Button variant="ghost" onClick={() => {
            setShowCompareModal(false);
            setCompareVersions({});
          }}>
            Close
          </Button>
        }
      >
        {compareVersions.v1 && compareVersions.v2 && (
          <div className="space-y-6">
            {/* Summary */}
            <Card className="bg-surface-secondary">
              <h4 className="font-semibold mb-2">What Changed</h4>
              {(() => {
                const changes: string[] = [];
                const fields = [
                  'hazard', 'hazardous_situation', 'harm', 'failure_mode',
                  'severity', 'probability_of_harm', 'occurrence', 'detection',
                  'risk_score', 'risk_level',
                  'inherent_safety', 'protective_measures', 'information_for_safety',
                  'residual_severity', 'residual_probability_of_harm', 'residual_risk_score',
                  'benefit_risk_summary', 'overall_residual_risk_conclusion',
                  'risk_acceptability', 'risk_rationale'
                ];
                
                fields.forEach(field => {
                  const v1Val = (compareVersions.v1 as any)[field];
                  const v2Val = (compareVersions.v2 as any)[field];
                  if (v1Val !== v2Val) {
                    changes.push(field.replace(/_/g, ' '));
                  }
                });
                
                return (
                  <div>
                    <p className="text-sm text-text-secondary mb-2">
                      {changes.length} field{changes.length !== 1 ? 's' : ''} changed
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {changes.map((change, idx) => (
                        <Badge key={idx} variant="info" size="sm">{change}</Badge>
                      ))}
                    </div>
                  </div>
                );
              })()}
            </Card>

            {/* Side-by-side comparison */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-3">v{compareVersions.v1.version_number}</h4>
                <div className="space-y-3 text-sm">
                  <div>
                    <strong>Hazard:</strong>
                    <p className="text-text-secondary mt-1">{compareVersions.v1.hazard || '-'}</p>
                  </div>
                  <div>
                    <strong>Risk Score:</strong>
                    <Badge variant="info" className="ml-2">
                      {compareVersions.v1.risk_score || 'N/A'} ({compareVersions.v1.risk_level || 'N/A'})
                    </Badge>
                  </div>
                  <div>
                    <strong>Acceptability:</strong>
                    <p className="text-text-secondary mt-1">{compareVersions.v1.risk_acceptability || '-'}</p>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold mb-3">v{compareVersions.v2.version_number}</h4>
                <div className="space-y-3 text-sm">
                  <div>
                    <strong>Hazard:</strong>
                    <p className={`mt-1 ${
                      compareVersions.v1.hazard !== compareVersions.v2.hazard
                        ? 'bg-amber-500/20 p-2 rounded border border-amber-500/30'
                        : 'text-text-secondary'
                    }`}>
                      {compareVersions.v2.hazard || '-'}
                    </p>
                  </div>
                  <div>
                    <strong>Risk Score:</strong>
                    <Badge
                      variant={compareVersions.v1.risk_score !== compareVersions.v2.risk_score ? 'danger' : 'info'}
                      className="ml-2"
                    >
                      {compareVersions.v2.risk_score || 'N/A'} ({compareVersions.v2.risk_level || 'N/A'})
                    </Badge>
                  </div>
                  <div>
                    <strong>Acceptability:</strong>
                    <p className={`mt-1 ${
                      compareVersions.v1.risk_acceptability !== compareVersions.v2.risk_acceptability
                        ? 'bg-amber-500/20 p-2 rounded border border-amber-500/30'
                        : 'text-text-secondary'
                    }`}>
                      {compareVersions.v2.risk_acceptability || '-'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Approval Warning Modal */}
      <Modal
        isOpen={showApprovalWarning}
        onClose={() => setShowApprovalWarning(false)}
        title="Post-Approval Edit Warning"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowApprovalWarning(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                setShowApprovalWarning(false);
                // User needs to add rationale before saving
              }}
            >
              Continue with Edit
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-text-secondary">
            This risk item has an approved version. Creating a new version will require re-approval.
          </p>
          <p className="text-text-secondary">
            Please provide a <strong>Risk Rationale</strong> explaining why changes are needed after approval.
          </p>
        </div>
      </Modal>

      {/* Design Handoff Modal */}
      <Modal
        isOpen={showDesignHandoffModal}
        onClose={() => {
          setShowDesignHandoffModal(false);
          setSelectedControlForHandoff(null);
          setDesignHandoffType(null);
          setDesignHandoffData({});
        }}
        title={`Create Design Artifact from Control: ${selectedControlForHandoff?.control_name || ''}`}
        size="lg"
        footer={
          <>
            <Button
              variant="ghost"
              onClick={() => {
                setShowDesignHandoffModal(false);
                setSelectedControlForHandoff(null);
                setDesignHandoffType(null);
                setDesignHandoffData({});
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleDesignHandoff}
              disabled={!designHandoffType}
            >
              Create & Link
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-text-secondary mb-4">
            Select the type of design artifact to create from this control. The artifact will be automatically linked.
          </p>
          
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Artifact Type *
            </label>
            <div className="flex gap-4">
              <Button
                variant={designHandoffType === 'design_input' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setDesignHandoffType('design_input')}
              >
                Design Input
              </Button>
              <Button
                variant={designHandoffType === 'design_output' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setDesignHandoffType('design_output')}
              >
                Design Output
              </Button>
              <Button
                variant={designHandoffType === 'vv_test' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setDesignHandoffType('vv_test')}
              >
                V&V Test
              </Button>
            </div>
          </div>
          
          {designHandoffType && (
            <div className="space-y-4">
              <Input
                label="Name"
                value={designHandoffData.name || selectedControlForHandoff?.control_name || ''}
                onChange={(e) => setDesignHandoffData({ ...designHandoffData, name: e.target.value })}
                placeholder="Artifact name"
              />
              
              <Textarea
                label="Description"
                value={designHandoffData.description || selectedControlForHandoff?.control_description || ''}
                onChange={(e) => setDesignHandoffData({ ...designHandoffData, description: e.target.value })}
                rows={4}
                placeholder="Description will include risk context automatically"
              />
              
              {designHandoffType === 'vv_test' && (
                <>
                  <Input
                    label="Design Output ID *"
                    value={designHandoffData.design_output_id || ''}
                    onChange={(e) => setDesignHandoffData({ ...designHandoffData, design_output_id: e.target.value })}
                    placeholder="Required for V&V test"
                  />
                  <Input
                    label="Test Method"
                    value={designHandoffData.test_method || ''}
                    onChange={(e) => setDesignHandoffData({ ...designHandoffData, test_method: e.target.value })}
                  />
                  <Textarea
                    label="Acceptance Criteria"
                    value={designHandoffData.acceptance_criteria || ''}
                    onChange={(e) => setDesignHandoffData({ ...designHandoffData, acceptance_criteria: e.target.value })}
                    rows={2}
                  />
                </>
              )}
            </div>
          )}
        </div>
      </Modal>

      {/* CAPA Handoff Modal */}
      <Modal
        isOpen={showCAPAHandoffModal}
        onClose={() => {
          setShowCAPAHandoffModal(false);
          setCapaHandoffData({});
        }}
        title="Create CAPA from Risk Item"
        size="lg"
        footer={
          <>
            <Button
              variant="ghost"
              onClick={() => {
                setShowCAPAHandoffModal(false);
                setCapaHandoffData({});
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleCAPAHandoff}>
              Create CAPA & Link
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-text-secondary mb-4">
            Create a CAPA record pre-filled with risk information. A trace link will be automatically created.
          </p>
          
          <Input
            label="CAPA Title"
            value={capaHandoffData.title || (riskItem ? `CAPA: Mitigate ${riskItem.title}` : '')}
            onChange={(e) => setCapaHandoffData({ ...capaHandoffData, title: e.target.value })}
          />
          
          <Textarea
            label="Root Cause"
            value={capaHandoffData.root_cause || ''}
            onChange={(e) => setCapaHandoffData({ ...capaHandoffData, root_cause: e.target.value })}
            rows={4}
            placeholder="Will be pre-filled with risk chain information"
          />
          
          <Textarea
            label="CAPA Plan"
            value={capaHandoffData.capa_plan || ''}
            onChange={(e) => setCapaHandoffData({ ...capaHandoffData, capa_plan: e.target.value })}
            rows={4}
            placeholder="Corrective and preventive action plan"
          />
        </div>
      </Modal>

      {/* Change Control Handoff Modal */}
      <Modal
        isOpen={showChangeHandoffModal}
        onClose={() => {
          setShowChangeHandoffModal(false);
          setChangeHandoffVersionId(null);
        }}
        title="Create Change Request from Version"
        size="lg"
        footer={
          <>
            <Button
              variant="ghost"
              onClick={() => {
                setShowChangeHandoffModal(false);
                setChangeHandoffVersionId(null);
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleChangeHandoff}>
              Create Change Control & Link
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-text-secondary mb-4">
            Create a Change Control record from this risk version. The change summary will include version diff information.
          </p>
          
          {changeHandoffVersionId && (
            <div className="p-3 bg-surface-secondary rounded-lg mb-4">
              <div className="text-sm font-medium mb-1">Selected Version:</div>
              <div className="text-text-secondary">
                {versions.find(v => v.id === changeHandoffVersionId)?.version_number 
                  ? `v${versions.find(v => v.id === changeHandoffVersionId)!.version_number}`
                  : 'Current Version'}
              </div>
            </div>
          )}
          
          <p className="text-sm text-text-secondary">
            Change Control will be pre-filled with:
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Risk key and version number</li>
              <li>Change summary from version diff</li>
              <li>List of impacted artifacts from trace links</li>
            </ul>
          </p>
        </div>
      </Modal>

      <GenerateVVModal
        open={vvModalOpen}
        onClose={closeVVModal}
        data={vvData}
        loading={vvLoading}
        error={vvError}
        onRetry={openGenerateVV}
        projectId={finalProjectId || null}
        riskItemId={riskItemId ?? null}
      />
    </div>
  );
};

export default RiskItemDetailPage;

