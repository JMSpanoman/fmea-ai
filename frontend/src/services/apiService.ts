// src/services/apiService.ts
import api from '../axios';

// Types
export interface Project {
  id: string; // UUID
  name: string;
  description?: string | null;
  user_id: string; // UUID
  created_at: string;
  updated_at?: string | null;

  // Backward-compatible optional fields (some legacy pages expect these)
  status?: string;
  version_number?: string;
  major_version?: number;
  minor_version?: number;
  patch_version?: number;
  version_status?: string;
  version_label?: string | null;
  change_summary?: string | null;
  change_details?: any | null;
  content_hash?: string | null;
  approval_required?: string;
  approved_by?: string | null;
  approved_at?: string | null;
  version_created_at?: string;
  version_updated_at?: string;
}

export interface FMEA {
  id: number;
  project_id: number;
  user_id: string;
  component: string;
  failure_mode: string;
  potential_effects: string;
  severity: number;
  potential_causes: string;
  occurrence: number;
  current_controls: string;
  detection: number;
  rpn: number;
  recommended_actions: string;
  responsibility: string;
  target_completion_date: string;
  actions_taken: string;
  final_severity: number;
  final_occurrence: number;
  final_detection: number;
  final_rpn: number;
  created_at: string;
  updated_at: string;
}

export interface CapaData {
  id: string;
  issue_description: string;
  source: string;
  detection_date: string;
  severity: string;
  root_cause: string;
  corrective_action: string;
  preventive_action: string;
  action_owner: string;
  due_date: string;
  status: string;
  effectiveness_check_plan: string;
  fmea_link: string;
  regulatory_impact: string;
  closure_summary: string;
  milestones: string;
  risk_controls_update: string;
  analysis_timestamp: string;
  version: string;
}

export interface CapaResponse {
  capa_data: CapaData[];
  mock: boolean;
}

export interface ChangeControlData {
  id: string;
  change_description: string;
  initiator: string;
  date_initiated: string;
  status: string;
  impact_assessment: string;
  actions_required: string;
  action_owner: string;
  due_date: string;
  closure_summary: string;
  analysis_timestamp: string;
  version: string;
}

export interface ChangeControlResponse {
  change_control_data: ChangeControlData[];
  mock: boolean;
}

// Fetch all projects
export const getProjects = async (): Promise<Project[]> => {
  try {
    console.log('ApiService: Calling api.get("/projects")...');
    const response = await api.get('/projects');
    console.log('ApiService: Projects response:', response.data);
    return response.data;
  } catch (error) {
    console.error('ApiService: Error fetching projects:', error);
    throw error;
  }
};

// Create a new project
export const createProject = async (projectData: { name: string; description?: string }): Promise<Project> => {
  try {
    const response = await api.post('/projects', projectData);
    return response.data;
  } catch (error) {
    console.error('Error creating project:', error);
    throw error;
  }
};

// Fetch all FMEAs
export const getFmeas = async (): Promise<FMEA[]> => {
  try {
    const response = await api.get('/fmeas');
    return response.data;
  } catch (error) {
    console.error('Error fetching FMEAs:', error);
    throw error;
  }
};

// Create a new FMEA
export const createFmea = async (fmeaData: any): Promise<FMEA> => {
  try {
    const response = await api.post('/fmeas', fmeaData);
    return response.data;
  } catch (error) {
    console.error('Error creating FMEA:', error);
    throw error;
  }
};

// Generate CAPA
export const generateCapa = async (issueDescription: string, capaType: string = 'corrective'): Promise<CapaResponse> => {
  try {
    const response = await api.post('/fmea/capa/generate', {
      issue_description: issueDescription,
      capa_type: capaType
    });
    return response.data;
  } catch (error) {
    console.error('Error generating CAPA:', error);
    throw error;
  }
};

// Generate Design Inputs
export interface DesignInputItem {
  title: string;
  requirement: string;
  description?: string;
}

export interface DesignInputsGenerateResponse {
  design_inputs: DesignInputItem[];
}

export const generateDesignInputs = async (componentName: string, count: number = 5): Promise<DesignInputsGenerateResponse> => {
  try {
    const response = await api.post('/ai/design-inputs/generate', {
      component_name: componentName,
      count: count
    });
    return response.data;
  } catch (error) {
    console.error('Error generating design inputs:', error);
    throw error;
  }
};

// Generate Design Outputs
export interface DesignOutputItem {
  title: string;
  specification: string;
  description?: string;
}

export interface DesignOutputsGenerateResponse {
  design_outputs: DesignOutputItem[];
}

export const generateDesignOutputs = async (componentName: string, count: number = 5): Promise<DesignOutputsGenerateResponse> => {
  try {
    const response = await api.post('/ai/design-outputs/generate', {
      component_name: componentName,
      count: count
    });
    return response.data;
  } catch (error) {
    console.error('Error generating design outputs:', error);
    throw error;
  }
};

// Health check for CAPA
export const capaHealth = async (): Promise<{ status: string; message: string }> => {
  try {
    const response = await api.get('/fmea/capa/health');
    return response.data;
  } catch (error) {
    console.error('Error checking CAPA health:', error);
    throw error;
  }
};

// Generate Change Control
export const generateChangeControl = async (changeDescription: string): Promise<ChangeControlResponse> => {
  try {
    console.log('Making API call to /fmea/change-control/generate with:', { change_description: changeDescription });
    const response = await api.post('/fmea/change-control/generate', {
      change_description: changeDescription
    });
    console.log('API response received:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Error generating Change Control:', error);
    console.error('Error details:', error.response?.data || error.message);
    throw error;
  }
};

// Risk Management Plan (RMP) Types and API
export interface ComponentInput {
  name: string;
  description?: string;
}

export interface RMPGenerateRequest {
  title?: string;
  scope: string;
  intended_use: string;
  components: ComponentInput[];
  acceptability_profile?: string;
  custom_acceptability_criteria?: any;
  review_roles: { [key: string]: string };
  ai_assistance_enabled?: boolean;
}

export interface RMPOut {
  id: string;
  project_id: string;
  title: string;
  scope: string;
  intended_use: string;
  components_json: string;
  acceptability_criteria_json: string;
  risk_methodology: string;
  review_roles_json: string;
  risk_control_categories_json: string;
  benefit_risk_criteria: string;
  lifecycle_linkage: string;
  governance_rules: string;
  rendered_html: string;
  status: string;
  current_version_no: number;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

export interface RMPApprovalRequest {
  decision: 'approved' | 'rejected';
  rationale: string;
}

// RMP API methods
export const generateRMP = async (projectId: string, request: RMPGenerateRequest): Promise<RMPOut> => {
  try {
    const response = await api.post(`/projects/${projectId}/risk-management-plan/generate`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error generating RMP:', error);
    throw error;
  }
};

export const getRMP = async (projectId: string): Promise<RMPOut> => {
  try {
    const response = await api.get(`/projects/${projectId}/risk-management-plan`);
    return response.data;
  } catch (error: any) {
    console.error('Error getting RMP:', error);
    throw error;
  }
};

export const updateRMP = async (projectId: string, rmpId: string, request: Partial<RMPGenerateRequest>): Promise<RMPOut> => {
  try {
    const response = await api.put(`/projects/${projectId}/risk-management-plan/${rmpId}`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error updating RMP:', error);
    throw error;
  }
};

export const approveRMP = async (projectId: string, rmpId: string, request: RMPApprovalRequest): Promise<any> => {
  try {
    const response = await api.post(`/projects/${projectId}/risk-management-plan/${rmpId}/approve`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error approving RMP:', error);
    throw error;
  }
};

export const exportRMPHTML = async (projectId: string, rmpId: string): Promise<string> => {
  try {
    const response = await api.get(`/projects/${projectId}/risk-management-plan/${rmpId}/export/html`, {
      responseType: 'text'
    });
    return response.data;
  } catch (error: any) {
    console.error('Error exporting RMP HTML:', error);
    throw error;
  }
};

// Risk Management File (RMF) Types and API
export interface ComponentFilter {
  id?: string;
  name: string;
}

export interface RMFGenerateRequest {
  components?: ComponentFilter[];
  include_ai_events?: boolean;
  include_audit_log?: boolean;
  include_traceability?: boolean;
  format?: string;
}

export interface RMFGenerateResponse {
  project_id: string;
  components: ComponentFilter[];
  generated_at: string;
  rmf_html: string;
}

export interface RMFEvidence {
  project_id: string;
  components: ComponentFilter[];
  risks: any[];
  summaries?: {
    risk_count: number;
    total_versions: number;
    total_controls: number;
    total_approvals: number;
    generated_at: string;
  };
}

// RMF API methods
export const generateRMF = async (projectId: string, request: RMFGenerateRequest): Promise<RMFGenerateResponse> => {
  try {
    const response = await api.post(`/projects/${projectId}/rmf/generate`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error generating RMF:', error);
    throw error;
  }
};

export const exportRMF = async (
  projectId: string,
  components?: string,
  includeAiEvents: boolean = true,
  includeAuditLog: boolean = true,
  includeTraceability: boolean = true
): Promise<string> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    params.append('include_ai_events', includeAiEvents.toString());
    params.append('include_audit_log', includeAuditLog.toString());
    params.append('include_traceability', includeTraceability.toString());
    
    const response = await api.get(`/projects/${projectId}/rmf/export?${params.toString()}`, {
      responseType: 'text'
    });
    return response.data;
  } catch (error: any) {
    console.error('Error exporting RMF HTML:', error);
    throw error;
  }
};

export const getRMFEvidence = async (
  projectId: string,
  components?: string,
  includeAiEvents: boolean = true,
  includeAuditLog: boolean = true,
  includeTraceability: boolean = true
): Promise<RMFEvidence> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    params.append('include_ai_events', includeAiEvents.toString());
    params.append('include_audit_log', includeAuditLog.toString());
    params.append('include_traceability', includeTraceability.toString());
    
    const response = await api.get(`/projects/${projectId}/rmf/evidence?${params.toString()}`);
    return response.data;
  } catch (error: any) {
    console.error('Error getting RMF evidence:', error);
    throw error;
  }
};

// Hazard Analysis Types and API
export interface HazardAnalysisGenerateRequest {
  components?: ComponentFilter[];
  version_scope?: 'approved_only' | 'current' | 'all' | 'include_draft' | 'latest_versions';
  include_unapproved?: boolean;
  report_mode?: 'regulatory' | 'working';
  include_metadata?: boolean;
  include_ai_assist_summary?: boolean;
  format?: string;
}

export interface HazardAnalysisGenerateResponse {
  project_id: string;
  components: ComponentFilter[];
  generated_at: string;
  version_scope: string;
  report_mode?: string;
  hazard_analysis_html: string;
  counts: {
    risk_items: number;
    versions_included: number;
    unapproved_excluded: number;
  };
}

export interface HazardAnalysisRow {
  id?: string;
  risk_item_id?: string;
  risk_item_version_id?: string;
  risk_key: string;
  version_id?: string;
  version_no: number;
  component_name: string;
  hazard_category?: string | null;
  hazard: string | null;
  foreseeable_sequence_of_events?: string | null;
  sequence_of_events?: string | null;
  hazardous_situation: string | null;
  harm: string | null;
  sequence_of_events?: string | null;
  affected_user?: string | null;
  failure_mode: string | null;
  cause_of_failure?: string | null;
  clinical_effect?: string | null;
  operating_mode?: string | null;
  use_environment?: string | null;
  initial_severity?: number | null;
  initial_probability?: number | null;
  initial_occurrence?: number | null;
  initial_risk_level?: string | null;
  risk_control_measures?: string[] | null;
  risk_control_type?: string[] | null;
  control_implementation_notes?: string | null;
  risk_controls?: Array<{
    control_type: string;
    control_description: string;
    implementation_status?: string | null;
    verification_method?: string | null;
    verification_status?: string | null;
  }> | null;
  residual_severity?: number | null;
  residual_probability?: number | null;
  residual_occurrence?: number | null;
  residual_risk_level?: string | null;
  residual_risk_acceptability?: string | null;
  risk_acceptability_decision?: string | null;
  risk_acceptability_justification?: string | null;
  benefit_risk_analysis_required?: boolean | null;
  benefit_risk_justification?: string | null;
  related_design_input?: string[] | null;
  related_design_output?: string[] | null;
  verification_reference?: string[] | null;
  validation_reference?: string[] | null;
  capa_reference?: string[] | null;
  requirement_ids?: string[] | null;
  approval_status?: string | null;
  approved: boolean;
  approved_at: string | null;
  approved_by: string | null;
  approver_role?: string | null;
  approval_meaning?: string | null;
  version_lock?: boolean;
  review_date?: string | null;
  review_frequency?: string | null;
  last_reviewed_by?: string | null;
  post_market_trigger?: boolean;
  reviewer_comments?: string | null;
  ai_generated?: boolean | null;
  ai_confidence?: string | null;
  source_context?: string | null;
  assumptions?: string[] | null;
  is_current?: boolean;
}

// Hazard Analysis API methods
export const generateHazardAnalysis = async (
  projectId: string,
  request: HazardAnalysisGenerateRequest
): Promise<HazardAnalysisGenerateResponse> => {
  try {
    const response = await api.post(`/projects/${projectId}/hazard-analysis/generate`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error generating Hazard Analysis:', error);
    throw error;
  }
};

export const exportHazardAnalysis = async (
  projectId: string,
  components?: string,
  versionScope: string = 'approved_only',
  includeUnapproved: boolean = false,
  reportMode: 'regulatory' | 'working' = 'regulatory'
): Promise<string> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    params.append('version_scope', versionScope);
    params.append('include_unapproved', includeUnapproved.toString());
    params.append('report_mode', reportMode);
    
    const response = await api.get(`/projects/${projectId}/hazard-analysis/export?${params.toString()}`, {
      responseType: 'text'
    });
    return response.data;
  } catch (error: any) {
    console.error('Error exporting Hazard Analysis HTML:', error);
    throw error;
  }
};

export const getHazardAnalysisData = async (
  projectId: string,
  components?: string,
  versionScope: string = 'approved_only',
  includeUnapproved: boolean = false,
  reportMode: 'regulatory' | 'working' = 'regulatory'
): Promise<HazardAnalysisRow[]> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    params.append('version_scope', versionScope);
    params.append('include_unapproved', includeUnapproved.toString());
    params.append('report_mode', reportMode);
    const response = await api.get(`/projects/${projectId}/hazard-analysis/data?${params.toString()}`);
    return response.data;
  } catch (error: any) {
    console.error('Error getting Hazard Analysis data:', error);
    throw error;
  }
};

// Hazard Analysis Items (full ISO 14971 schema)
export const listHazardAnalysisItems = async (
  projectId: string,
  params?: { component_id?: string; approval_status?: string; hazard_category?: string; include_draft?: boolean }
): Promise<HazardAnalysisRow[]> => {
  const q = new URLSearchParams();
  if (params?.component_id) q.append('component_id', params.component_id);
  if (params?.approval_status) q.append('approval_status', params.approval_status);
  if (params?.hazard_category) q.append('hazard_category', params.hazard_category);
  if (params?.include_draft === false) q.append('include_draft', 'false');
  const response = await api.get(`/projects/${projectId}/hazard-analysis/items?${q.toString()}`);
  return response.data;
};

export const createHazardAnalysisItem = async (
  projectId: string,
  payload: { project_id: string; component_id?: string; risk_key?: string; hazard?: string; failure_mode?: string; [key: string]: any }
): Promise<{ id: string; project_id: string; risk_key: string }> => {
  const response = await api.post(`/projects/${projectId}/hazard-analysis/items`, { ...payload, project_id: projectId });
  return response.data;
};

export const fillGapsHazardAnalysisItem = async (
  projectId: string,
  itemId: string
): Promise<{ id: string; ai_confidence: string }> => {
  const response = await api.post(`/projects/${projectId}/hazard-analysis/items/${itemId}/fill-gaps`);
  return response.data;
};

export const syncHazardAnalysisFromFmea = async (
  projectId: string,
  componentId?: string
): Promise<{ project_id: string; created: number; fmea_rows_processed: number }> => {
  const q = componentId ? `?component_id=${encodeURIComponent(componentId)}` : '';
  const response = await api.post(`/projects/${projectId}/hazard-analysis/items/sync-from-fmea${q}`);
  return response.data;
};

export const approveHazardAnalysisItem = async (
  projectId: string,
  itemId: string
): Promise<{ id: string; approval_status: string }> => {
  const response = await api.post(`/projects/${projectId}/hazard-analysis/items/${itemId}/approve`);
  return response.data;
};

// Residual Risk Evaluation Types and API
export interface ResidualRiskGenerateRequest {
  components?: ComponentFilter[];
  version_scope?: 'approved_only' | 'current' | 'all';
  include_unapproved?: boolean;
  acceptability_profile?: string;
  custom_thresholds?: any;
  format?: string;
}

export interface ResidualRiskGenerateResponse {
  project_id: string;
  components: ComponentFilter[];
  generated_at: string;
  version_scope: string;
  residual_risk_html: string;
  counts: {
    versions_included: number;
    missing_residual_fields: number;
    excluded_versions?: number;
  };
  finalDetermination?: string;
  dataQualityStatus?: string;
  reportStatus?: string;
  completenessScore?: number;
  totalRiskItems?: number;
  totalHazards?: number;
  missingFieldCounts?: Record<string, number>;
  traceabilitySummary?: Record<string, number>;
  riskReductionSummary?: Record<string, any>;
  regulatoryObservations?: string[];
  benefitRiskRequiredCount?: number;
  unacceptableResidualRiskCount?: number;
}

export interface ResidualRiskRow {
  risk_item_id: string;
  risk_key: string;
  version_id: string;
  version_no: number;
  component_name: string;
  residual_severity: number | null;
  residual_probability_of_harm: number | null;
  residual_risk_score: number | null;
  residual_acceptability: string;
  acceptability_source: 'stored' | 'inferred';
  approved: boolean;
  approved_at: string | null;
  approved_by: string | null;
  is_current: boolean;
}

// Residual Risk Evaluation API methods
export const generateResidualRisk = async (
  projectId: string,
  request: ResidualRiskGenerateRequest
): Promise<ResidualRiskGenerateResponse> => {
  try {
    const response = await api.post(`/projects/${projectId}/residual-risk/generate`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error generating Residual Risk Evaluation:', error);
    throw error;
  }
};

export const exportResidualRisk = async (
  projectId: string,
  components?: string,
  versionScope: string = 'approved_only',
  includeUnapproved: boolean = false
): Promise<string> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    params.append('version_scope', versionScope);
    params.append('include_unapproved', includeUnapproved.toString());
    
    const response = await api.get(`/projects/${projectId}/residual-risk/export?${params.toString()}`, {
      responseType: 'text'
    });
    return response.data;
  } catch (error: any) {
    console.error('Error exporting Residual Risk Evaluation HTML:', error);
    throw error;
  }
};

export const getResidualRiskData = async (
  projectId: string,
  components?: string,
  versionScope: string = 'approved_only',
  includeUnapproved: boolean = false
): Promise<ResidualRiskRow[]> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    params.append('version_scope', versionScope);
    params.append('include_unapproved', includeUnapproved.toString());
    
    const response = await api.get(`/projects/${projectId}/residual-risk/data?${params.toString()}`);
    return response.data;
  } catch (error: any) {
    console.error('Error getting Residual Risk Evaluation data:', error);
    throw error;
  }
};

// Risk Control Measures Documentation Types and API
export interface RiskControlsDocGenerateRequest {
  components?: ComponentFilter[];
  include_only_active_controls?: boolean;
  version_scope?: string;
  include_traceability_details?: boolean;
  format?: string;
}

export interface RiskControlsDocGenerateResponse {
  project_id: string;
  components: ComponentFilter[];
  generated_at: string;
  risk_controls_doc_html: string;
  counts: {
    controls: number;
    missing_implementation: number;
    missing_verification: number;
  };
}

export interface RiskControlsDocRow {
  risk_item_id: string;
  risk_key: string;
  component_name: string;
  hazard: string | null;
  harm: string | null;
  control_id: string;
  control_key: string;
  control_name: string;
  control_type: string;
  control_status: string;
  control_description: string | null;
  implementation_details: string | null;
  verification_method: string | null;
  implementation_refs: Array<{
    type: string;
    id: string;
    display: string;
    link_type?: string;
    created_at?: string;
  }>;
  verification_methods: Array<{
    type: string;
    id: string;
    display: string;
    link_type?: string;
    created_at?: string;
  }>;
  flags: {
    missing_implementation: boolean;
    missing_verification: boolean;
  };
}

// Risk Control Measures Documentation API methods
export const generateRiskControlsDoc = async (
  projectId: string,
  request: RiskControlsDocGenerateRequest
): Promise<RiskControlsDocGenerateResponse> => {
  try {
    const response = await api.post(`/projects/${projectId}/risk-controls-doc/generate`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error generating Risk Control Measures Documentation:', error);
    throw error;
  }
};

export const exportRiskControlsDoc = async (
  projectId: string,
  components?: string,
  activeOnly: boolean = true
): Promise<string> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    params.append('active_only', activeOnly.toString());
    
    const response = await api.get(`/projects/${projectId}/risk-controls-doc/export?${params.toString()}`, {
      responseType: 'text'
    });
    return response.data;
  } catch (error: any) {
    console.error('Error exporting Risk Control Measures Documentation HTML:', error);
    throw error;
  }
};

export const getRiskControlsDocData = async (
  projectId: string,
  components?: string,
  activeOnly: boolean = true
): Promise<RiskControlsDocRow[]> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    params.append('active_only', activeOnly.toString());
    
    const response = await api.get(`/projects/${projectId}/risk-controls-doc/data?${params.toString()}`);
    return response.data;
  } catch (error: any) {
    console.error('Error getting Risk Control Measures Documentation data:', error);
    throw error;
  }
};

// Reports - Risk Control Measures API (alternative endpoint structure)
export interface RiskControlMeasuresDataResponse {
  project_id: string;
  components: ComponentFilter[];
  generated_at: string;
  rows: Array<{
    risk_item_id: string;
    risk_key: string;
    control_id: string;
    control_key: string;
    control_name: string;
    control_type: string;
    control_description: string;
    control_status: string;
    implementation_refs: Array<{
      artifact_type: string;
      artifact_id: string;
      display: string;
      link_type?: string;
    }>;
    verification_methods: Array<{
      artifact_type: string;
      artifact_id: string;
      display: string;
      link_type?: string;
    }>;
    flags: {
      missing_implementation: boolean;
      missing_verification: boolean;
    };
  }>;
  counts: {
    controls: number;
    missing_implementation: number;
    missing_verification: number;
  };
}

export const getRiskControlMeasuresData = async (
  projectId: string,
  components?: string,
  activeOnly: boolean = true
): Promise<RiskControlMeasuresDataResponse> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    params.append('active_only', activeOnly.toString());
    
    const response = await api.get(`/projects/${projectId}/reports/risk-control-measures/data?${params.toString()}`);
    return response.data;
  } catch (error: any) {
    console.error('Error getting Risk Control Measures data:', error);
    throw error;
  }
};

// PMS Signal Types and API
export interface PMSSignal {
  id: string;
  project_id: string;
  signal_key: string;
  signal_type: string;
  component_names_json: string[];
  title: string;
  description?: string;
  source_ref?: string;
  date_detected: string;
  severity_observed?: number;
  frequency_observed?: number;
  rate_observed?: number;
  trend_status: string;
  trigger_status: string;
  recommended_action?: string;
  owner?: string;
  status: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

export interface PMSSignalCreate {
  signal_key: string;
  signal_type: string;
  component_names_json: string[];
  title: string;
  description?: string;
  source_ref?: string;
  date_detected: string;
  severity_observed?: number;
  frequency_observed?: number;
  rate_observed?: number;
  trend_status?: string;
  trigger_status?: string;
  recommended_action?: string;
  owner?: string;
  status?: string;
}

export interface PMSSignalUpdate {
  signal_key?: string;
  signal_type?: string;
  component_names_json?: string[];
  title?: string;
  description?: string;
  source_ref?: string;
  date_detected?: string;
  severity_observed?: number;
  frequency_observed?: number;
  rate_observed?: number;
  trend_status?: string;
  trigger_status?: string;
  recommended_action?: string;
  owner?: string;
  status?: string;
}

export interface PMSSignalLinkRiskRequest {
  risk_item_id: string;
  link_type?: string;
}

export interface PMSSignalHandoffCAPARequest {
  capa_title?: string;
  capa_description?: string;
}

export interface PMSSignalHandoffChangeRequest {
  change_title?: string;
  change_description?: string;
}

export interface PMSSignalReportGenerateRequest {
  components?: ComponentFilter[];
  date_from?: string;
  date_to?: string;
  include_open_only?: boolean;
  include_traceability?: boolean;
  include_actions?: boolean;
  format?: string;
}

export interface PMSSignalReportGenerateResponse {
  project_id: string;
  components: ComponentFilter[];
  generated_at: string;
  pms_report_html: string;
  counts: any;
  summary: any;
}

// PMS Signal CRUD API methods
export const createPMSSignal = async (
  projectId: string,
  signal: PMSSignalCreate
): Promise<PMSSignal> => {
  try {
    const response = await api.post(`/projects/${projectId}/pms/signals`, signal);
    return response.data;
  } catch (error: any) {
    console.error('Error creating PMS signal:', error);
    throw error;
  }
};

export const getPMSSignals = async (
  projectId: string,
  component?: string,
  signalType?: string,
  status?: string,
  dateFrom?: string,
  dateTo?: string
): Promise<PMSSignal[]> => {
  try {
    const params = new URLSearchParams();
    if (component) params.append('component', component);
    if (signalType) params.append('signal_type', signalType);
    if (status) params.append('status', status);
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    
    const response = await api.get(`/projects/${projectId}/pms/signals?${params.toString()}`);
    return response.data;
  } catch (error: any) {
    console.error('Error getting PMS signals:', error);
    throw error;
  }
};

export const getPMSSignal = async (
  projectId: string,
  signalId: string
): Promise<PMSSignal> => {
  try {
    const response = await api.get(`/projects/${projectId}/pms/signals/${signalId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error getting PMS signal:', error);
    throw error;
  }
};

export const updatePMSSignal = async (
  projectId: string,
  signalId: string,
  signalUpdate: PMSSignalUpdate
): Promise<PMSSignal> => {
  try {
    const response = await api.put(`/projects/${projectId}/pms/signals/${signalId}`, signalUpdate);
    return response.data;
  } catch (error: any) {
    console.error('Error updating PMS signal:', error);
    throw error;
  }
};

export const deletePMSSignal = async (
  projectId: string,
  signalId: string
): Promise<void> => {
  try {
    await api.delete(`/projects/${projectId}/pms/signals/${signalId}`);
  } catch (error: any) {
    console.error('Error deleting PMS signal:', error);
    throw error;
  }
};

// PMS Signal Handoff API methods
export const linkPMSSignalToRisk = async (
  projectId: string,
  signalId: string,
  request: PMSSignalLinkRiskRequest
): Promise<any> => {
  try {
    const response = await api.post(`/projects/${projectId}/pms/signals/${signalId}/link/risk-item`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error linking PMS signal to risk:', error);
    throw error;
  }
};

export const handoffPMSSignalToCAPA = async (
  projectId: string,
  signalId: string,
  request: PMSSignalHandoffCAPARequest
): Promise<any> => {
  try {
    const response = await api.post(`/projects/${projectId}/pms/signals/${signalId}/handoff/capa`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error creating CAPA from PMS signal:', error);
    throw error;
  }
};

export const handoffPMSSignalToChange = async (
  projectId: string,
  signalId: string,
  request: PMSSignalHandoffChangeRequest
): Promise<any> => {
  try {
    const response = await api.post(`/projects/${projectId}/pms/signals/${signalId}/handoff/change`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error creating Change Control from PMS signal:', error);
    throw error;
  }
};

// PMS Signal Report API methods
export const generatePMSSignalReport = async (
  projectId: string,
  request: PMSSignalReportGenerateRequest
): Promise<PMSSignalReportGenerateResponse> => {
  try {
    const response = await api.post(`/projects/${projectId}/pms/reports/signal-feedback/generate`, request);
    return response.data;
  } catch (error: any) {
    console.error('Error generating PMS Signal Report:', error);
    throw error;
  }
};

export const exportPMSSignalReport = async (
  projectId: string,
  components?: string,
  dateFrom?: string,
  dateTo?: string,
  includeOpenOnly: boolean = false,
  includeTraceability: boolean = true,
  includeActions: boolean = true
): Promise<string> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    params.append('include_open_only', includeOpenOnly.toString());
    params.append('include_traceability', includeTraceability.toString());
    params.append('include_actions', includeActions.toString());
    params.append('format', 'html');
    
    const response = await api.get(`/projects/${projectId}/pms/reports/signal-feedback/export?${params.toString()}`, {
      responseType: 'text'
    });
    return response.data;
  } catch (error: any) {
    console.error('Error exporting PMS Signal Report HTML:', error);
    throw error;
  }
};

export const exportRiskControlMeasuresHtml = async (
  projectId: string,
  components?: string,
  activeOnly: boolean = true
): Promise<string> => {
  try {
    const params = new URLSearchParams();
    if (components) params.append('components', components);
    params.append('active_only', activeOnly.toString());
    params.append('format', 'html');
    
    const response = await api.get(`/projects/${projectId}/reports/risk-control-measures/export?${params.toString()}`, {
      responseType: 'text'
    });
    return response.data;
  } catch (error: any) {
    console.error('Error exporting Risk Control Measures HTML:', error);
    throw error;
  }
}; 

// -----------------------------
// Design Inputs Documentation Report (Risk Control → Requirement)
// -----------------------------

export interface DesignInputsReportRow {
  di_id: string;
  di_key: string;
  title: string;
  requirement_text: string;
  status: string;
  acceptance_criteria?: string | null;
  updated_at?: string | null;
  upstream: {
    risk_controls: Array<{
      control_id: string;
      control_key: string;
      control_name: string;
      name?: string;
      link_type?: string;
      created_at?: string | null;
    }>;
    risks: Array<{
      risk_item_id: string;
      risk_key: string;
      hazard?: string | null;
      harm?: string | null;
    }>;
  };
  downstream: {
    design_outputs: Array<{
      id: string;
      do_key: string;
      title: string;
    }>;
    vv_tests: Array<{
      id: string;
      vv_key: string;
      title: string;
    }>;
  };
  completeness: {
    has_upstream_control: boolean;
    has_output: boolean;
    has_verification: boolean;
  };
}

export interface DesignInputsReportDataResponse {
  project_id: string;
  components: Array<{ id?: string; name?: string }>;
  generated_at?: string | null;
  rows: DesignInputsReportRow[];
  counts: {
    design_inputs: number;
    missing_output: number;
    missing_verification: number;
    missing_upstream_control: number;
  };
}

export const getDesignInputsReportData = async (
  projectId: string,
  components?: string,
  status?: string,
  includeUnlinked: boolean = false,
  missingOutput?: boolean,
  missingVerification?: boolean,
  search?: string
): Promise<DesignInputsReportDataResponse> => {
  const params = new URLSearchParams();
  if (components) params.append('components', components);
  if (status) params.append('status', status);
  params.append('include_unlinked', includeUnlinked.toString());
  if (missingOutput !== undefined) params.append('missing_output', String(missingOutput));
  if (missingVerification !== undefined) params.append('missing_verification', String(missingVerification));
  if (search) params.append('search', search);

  const res = await api.get(`/projects/${projectId}/reports/design-inputs/data?${params.toString()}`);
  return res.data;
};

export const exportDesignInputsReportHtml = async (
  projectId: string,
  components?: string,
  status?: string,
  includeUnlinked: boolean = false,
  missingOutput?: boolean,
  missingVerification?: boolean,
  search?: string
): Promise<string> => {
  const params = new URLSearchParams();
  if (components) params.append('components', components);
  if (status) params.append('status', status);
  params.append('format', 'html');
  params.append('include_unlinked', includeUnlinked.toString());
  if (missingOutput !== undefined) params.append('missing_output', String(missingOutput));
  if (missingVerification !== undefined) params.append('missing_verification', String(missingVerification));
  if (search) params.append('search', search);

  const res = await api.get(`/projects/${projectId}/reports/design-inputs/export?${params.toString()}`);
  return res.data;
};

// -----------------------------
// V&V Evidence Report (component-scoped)
// -----------------------------

export interface VVEvidenceReportRow {
  vv_test_id: string;
  vv_key: string;
  title: string;
  test_type: string; // verification|validation (MVP: inferred)
  method: string; // inspection|test|analysis|simulation|other (MVP: inferred)
  acceptance_criteria: string;
  status: string;
  updated_at?: string | null;
  upstream: {
    design_outputs: Array<{ id: string; do_key: string; title: string }>;
    design_inputs: Array<{ id: string; di_key: string; title: string }>;
    risk_controls: Array<{ id: string; control_key: string; name: string }>;
    risk_items: Array<{ id: string; risk_key: string; hazard?: string | null; harm?: string | null }>;
  };
  evidence_strength: "preferred" | "allowed" | "shortcut";
  completeness: {
    has_design_output_link: boolean;
    has_acceptance_criteria: boolean;
    has_upstream_links: boolean;
  };
}

export interface VVEvidenceReportDataResponse {
  project_id: string;
  components: Array<{ id?: string; name?: string }>;
  generated_at?: string | null;
  rows: VVEvidenceReportRow[];
  counts: {
    tests: number;
    unlinked: number;
    missing_design_output_link: number;
    missing_acceptance_criteria: number;
    strength: { preferred: number; allowed: number; shortcut: number };
  };
}

export const getVVEvidenceReportData = async (
  projectId: string,
  components?: string,
  testType?: string,
  status?: string,
  unlinkedOnly?: boolean,
  missingAcceptanceCriteria?: boolean,
  missingDesignOutputLink?: boolean,
  search?: string
): Promise<VVEvidenceReportDataResponse> => {
  const params = new URLSearchParams();
  if (components) params.append('components', components);
  if (testType) params.append('test_type', testType);
  if (status) params.append('status', status);
  if (unlinkedOnly !== undefined) params.append('unlinked_only', String(unlinkedOnly));
  if (missingAcceptanceCriteria !== undefined) params.append('missing_acceptance_criteria', String(missingAcceptanceCriteria));
  if (missingDesignOutputLink !== undefined) params.append('missing_design_output_link', String(missingDesignOutputLink));
  if (search) params.append('search', search);

  const res = await api.get(`/projects/${projectId}/reports/vv-evidence/data?${params.toString()}`);
  return res.data;
};

export const exportVVEvidenceReportHtml = async (
  projectId: string,
  components?: string,
  testType?: string,
  status?: string,
  unlinkedOnly?: boolean,
  missingAcceptanceCriteria?: boolean,
  missingDesignOutputLink?: boolean,
  search?: string
): Promise<string> => {
  const params = new URLSearchParams();
  if (components) params.append('components', components);
  if (testType) params.append('test_type', testType);
  if (status) params.append('status', status);
  if (unlinkedOnly !== undefined) params.append('unlinked_only', String(unlinkedOnly));
  if (missingAcceptanceCriteria !== undefined) params.append('missing_acceptance_criteria', String(missingAcceptanceCriteria));
  if (missingDesignOutputLink !== undefined) params.append('missing_design_output_link', String(missingDesignOutputLink));
  if (search) params.append('search', search);
  params.append('format', 'html');

  const res = await api.get(`/projects/${projectId}/reports/vv-evidence/export?${params.toString()}`);
  return res.data;
};