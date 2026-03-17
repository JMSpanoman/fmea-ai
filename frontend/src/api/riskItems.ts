import api from '../axios';

// Types matching backend schemas
export interface RiskItem {
  id: string;
  project_id: string;
  fmea_row_id?: string;
  current_version_id?: string;
  title: string;
  description?: string;
  category?: string;
  risk_type?: string;
  severity?: number;
  probability?: number;
  impact?: number;
  risk_score?: number;
  risk_level?: string;
  mitigation_strategy?: string;
  control_measures?: string;
  residual_risk_score?: number;
  residual_risk_level?: string;
  owner?: string;
  status: string;
  priority?: string;
  source?: string;
  detected_date?: string;
  due_date?: string;
  closed_date?: string;
  ai_metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
  current_version?: RiskItemVersion;
}

export interface RiskItemVersion {
  id: string;
  risk_item_id: string;
  version_number: number;
  hazard?: string;
  hazardous_situation?: string;
  harm?: string;
  failure_mode?: string;
  sequence_of_events?: string;
  /** Risk Knowledge Base: link to hazard_library.id */
  hazard_library_id?: string;
  /** Risk Knowledge Base: link to harm_library.id */
  harm_library_id?: string;
  /** Risk Knowledge Base: link to risk_control_library.id */
  risk_control_library_id?: string;
  /** Risk Knowledge Base: link to verification_library.id */
  verification_library_id?: string;
  severity?: number;
  probability_of_harm?: number;
  occurrence?: number;
  detection?: number;
  probability?: number;
  impact?: number;
  risk_score?: number;
  risk_level?: string;
  inherent_safety?: string;
  protective_measures?: string;
  information_for_safety?: string;
  control_measures_summary?: string;
  residual_severity?: number;
  residual_probability_of_harm?: number;
  residual_occurrence?: number;
  residual_detection?: number;
  residual_risk_score?: number;
  residual_risk_level?: string;
  benefit_risk_summary?: string;
  overall_residual_risk_conclusion?: string;
  risk_acceptability?: string;
  risk_rationale?: string;
  change_summary?: string;
  changed_by?: string;
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface RiskControl {
  id: string;
  risk_item_id: string;
  project_id: string;
  control_name: string;
  control_description?: string;
  control_type: 'inherent_safety' | 'protective' | 'information';
  implementation_details?: string;
  verification_method?: string;
  trace_to_design_input?: string;
  trace_to_design_output?: string;
  trace_to_verification_test?: string;
  status: 'proposed' | 'active' | 'retired';
  owner?: string;
  assigned_to?: string;
  proposed_date?: string;
  implemented_date?: string;
  verified_date?: string;
  effectiveness_notes?: string;
  ai_metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface RiskItemCreate {
  project_id: string;
  fmea_row_id?: string;
  title: string;
  description?: string;
  category?: string;
  risk_type?: string;
  severity?: number;
  probability?: number;
  impact?: number;
  hazard?: string;
  hazardous_situation?: string;
  harm?: string;
  failure_mode?: string;
  hazard_library_id?: string;
  harm_library_id?: string;
  risk_control_library_id?: string;
  verification_library_id?: string;
  probability_of_harm?: number;
  occurrence?: number;
  detection?: number;
  mitigation_strategy?: string;
  control_measures?: string;
  residual_risk_score?: number;
  owner?: string;
  status?: string;
  priority?: string;
  source?: string;
  detected_date?: string;
  due_date?: string;
  risk_rationale?: string;
  ai_metadata?: Record<string, any>;
}

export interface RiskItemUpdate {
  title?: string;
  description?: string;
  category?: string;
  risk_type?: string;
  severity?: number;
  probability?: number;
  impact?: number;
  mitigation_strategy?: string;
  control_measures?: string;
  residual_risk_score?: number;
  owner?: string;
  status?: string;
  priority?: string;
  source?: string;
  detected_date?: string;
  due_date?: string;
  fmea_row_id?: string;
  ai_metadata?: Record<string, any>;
  hazard?: string;
  hazardous_situation?: string;
  harm?: string;
  failure_mode?: string;
  probability_of_harm?: number;
  occurrence?: number;
  detection?: number;
  inherent_safety?: string;
  protective_measures?: string;
  information_for_safety?: string;
  residual_severity?: number;
  residual_probability_of_harm?: number;
  residual_occurrence?: number;
  residual_detection?: number;
  benefit_risk_summary?: string;
  overall_residual_risk_conclusion?: string;
  risk_acceptability?: string;
  risk_rationale?: string;
  change_summary?: string;
  hazard_library_id?: string;
  harm_library_id?: string;
  risk_control_library_id?: string;
  verification_library_id?: string;
}

export interface RiskItemVersionCreate {
  hazard?: string;
  hazardous_situation?: string;
  harm?: string;
  hazard_library_id?: string;
  harm_library_id?: string;
  risk_control_library_id?: string;
  verification_library_id?: string;
  failure_mode?: string;
  sequence_of_events?: string;
  severity?: number;
  probability_of_harm?: number;
  occurrence?: number;
  detection?: number;
  probability?: number;
  impact?: number;
  inherent_safety?: string;
  protective_measures?: string;
  information_for_safety?: string;
  control_measures_summary?: string;
  residual_severity?: number;
  residual_probability_of_harm?: number;
  residual_occurrence?: number;
  residual_detection?: number;
  benefit_risk_summary?: string;
  overall_residual_risk_conclusion?: string;
  risk_acceptability?: string;
  risk_rationale?: string;
  change_summary?: string;
  ai_metadata?: Record<string, any>;
}

export interface RiskControlCreate {
  risk_item_id: string;
  project_id: string;
  control_name: string;
  control_description?: string;
  control_type: 'inherent_safety' | 'protective' | 'information';
  implementation_details?: string;
  verification_method?: string;
  trace_to_design_input?: string;
  trace_to_design_output?: string;
  trace_to_verification_test?: string;
  status?: 'proposed' | 'active' | 'retired';
  owner?: string;
  assigned_to?: string;
  proposed_date?: string;
  implemented_date?: string;
  verified_date?: string;
  effectiveness_notes?: string;
  ai_metadata?: Record<string, any>;
}

export interface RiskControlUpdate {
  control_name?: string;
  control_description?: string;
  control_type?: 'inherent_safety' | 'protective' | 'information';
  implementation_details?: string;
  verification_method?: string;
  trace_to_design_input?: string;
  trace_to_design_output?: string;
  trace_to_verification_test?: string;
  status?: 'proposed' | 'active' | 'retired';
  owner?: string;
  assigned_to?: string;
  proposed_date?: string;
  implemented_date?: string;
  verified_date?: string;
  effectiveness_notes?: string;
  ai_metadata?: Record<string, any>;
}

export interface RiskItemApprovalRequest {
  version_id: string;
  decision: 'approved' | 'rejected';
  rationale: string;
  comment?: string;
}

export interface TraceLink {
  id: string;
  project_id: string;
  from_type: string;
  from_id: string;
  to_type: string;
  to_id: string;
  created_at: string;
}

export interface TraceLinkCreate {
  to_type: string;
  to_id: string;
}

// Risk Items API
export async function listRiskItems(
  projectId: string,
  filters?: { status?: string; category?: string }
): Promise<RiskItem[]> {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.category) params.append('category', filters.category);
  
  const query = params.toString();
  const url = `/projects/${projectId}/risk-items${query ? `?${query}` : ''}`;
  const response = await api.get<RiskItem[]>(url);
  return response.data;
}

export async function createRiskItem(
  projectId: string,
  payload: RiskItemCreate
): Promise<RiskItem> {
  const response = await api.post<RiskItem>(
    `/projects/${projectId}/risk-items`,
    { ...payload, project_id: projectId }
  );
  return response.data;
}

export async function getRiskItem(
  projectId: string,
  riskItemId: string
): Promise<RiskItem> {
  const response = await api.get<RiskItem>(
    `/projects/${projectId}/risk-items/${riskItemId}`
  );
  return response.data;
}

export async function updateRiskItem(
  projectId: string,
  riskItemId: string,
  payload: RiskItemUpdate
): Promise<RiskItem> {
  const response = await api.put<RiskItem>(
    `/projects/${projectId}/risk-items/${riskItemId}`,
    payload
  );
  return response.data;
}

export async function deleteRiskItem(
  projectId: string,
  riskItemId: string
): Promise<void> {
  await api.delete(`/projects/${projectId}/risk-items/${riskItemId}`);
}

// Versions API
export async function createRiskVersion(
  projectId: string,
  riskItemId: string,
  payload: RiskItemVersionCreate
): Promise<RiskItemVersion> {
  const response = await api.post<RiskItemVersion>(
    `/projects/${projectId}/risk-items/${riskItemId}/versions`,
    payload
  );
  return response.data;
}

export async function listRiskVersions(
  projectId: string,
  riskItemId: string
): Promise<RiskItemVersion[]> {
  const response = await api.get<RiskItemVersion[]>(
    `/projects/${projectId}/risk-items/${riskItemId}/versions`
  );
  return response.data;
}

export async function getRiskVersion(
  projectId: string,
  riskItemId: string,
  versionId: string
): Promise<RiskItemVersion> {
  const response = await api.get<RiskItemVersion>(
    `/projects/${projectId}/risk-items/${riskItemId}/versions/${versionId}`
  );
  return response.data;
}

// Approvals API
export async function approveRiskVersion(
  projectId: string,
  riskItemId: string,
  payload: RiskItemApprovalRequest
): Promise<{ message: string; approval_id: string }> {
  const response = await api.post(
    `/projects/${projectId}/risk-items/${riskItemId}/approve`,
    payload
  );
  return response.data;
}

// Controls API
export async function createRiskControl(
  projectId: string,
  riskItemId: string,
  payload: RiskControlCreate
): Promise<RiskControl> {
  const response = await api.post<RiskControl>(
    `/projects/${projectId}/risk-items/${riskItemId}/controls`,
    { ...payload, risk_item_id: riskItemId, project_id: projectId }
  );
  return response.data;
}

export async function listRiskControls(
  projectId: string,
  riskItemId: string
): Promise<RiskControl[]> {
  const response = await api.get<RiskControl[]>(
    `/projects/${projectId}/risk-items/${riskItemId}/controls`
  );
  return response.data;
}

export async function getRiskControl(
  projectId: string,
  riskItemId: string,
  controlId: string
): Promise<RiskControl> {
  const response = await api.get<RiskControl>(
    `/projects/${projectId}/risk-items/${riskItemId}/controls/${controlId}`
  );
  return response.data;
}

export async function patchRiskControl(
  projectId: string,
  riskItemId: string,
  controlId: string,
  payload: RiskControlUpdate
): Promise<RiskControl> {
  const response = await api.patch<RiskControl>(
    `/projects/${projectId}/risk-items/${riskItemId}/controls/${controlId}`,
    payload
  );
  return response.data;
}

export async function deleteRiskControl(
  projectId: string,
  riskItemId: string,
  controlId: string
): Promise<void> {
  await api.delete(
    `/projects/${projectId}/risk-items/${riskItemId}/controls/${controlId}`
  );
}

// Trace Links API
export async function listRiskLinks(
  projectId: string,
  riskItemId: string
): Promise<{ from: TraceLink[]; to: TraceLink[] }> {
  const response = await api.get<{ from: TraceLink[]; to: TraceLink[] }>(
    `/projects/${projectId}/risk-items/${riskItemId}/links`
  );
  return response.data;
}

export async function createRiskLink(
  projectId: string,
  riskItemId: string,
  payload: TraceLinkCreate
): Promise<TraceLink> {
  const response = await api.post<TraceLink>(
    `/projects/${projectId}/risk-items/${riskItemId}/links`,
    payload
  );
  return response.data;
}

// AI Suggestions
export interface AIRiskSuggestions {
  severity?: number;
  probability_of_harm?: number;
  detection?: number;
  risk_score?: number;
  risk_level?: string;
  mitigation?: string;
  residual_severity?: number;
  residual_probability_of_harm?: number;
  residual_detection?: number;
  residual_risk_score?: number;
  residual_risk_level?: string;
}

export interface AIEvent {
  id: string;
  project_id: string;
  user_id: string;
  context_type: string;
  context_id?: string;
  prompt_name: string;
  input_summary?: string;
  output_json?: Record<string, any>;
  disposition?: string;
  disposition_notes?: string;
  created_at: string;
  disposed_at?: string;
}

export async function getAIRiskSuggestions(
  projectId: string,
  riskItemId: string,
  input: { hazard?: string; hazardous_situation?: string; harm?: string }
): Promise<{ suggestions: AIRiskSuggestions; ai_event_id: string }> {
  const response = await api.post<{ suggestions: AIRiskSuggestions; ai_event_id: string }>(
    `/projects/${projectId}/risk-items/${riskItemId}/ai/suggest`,
    input
  );
  return response.data;
}

export async function updateAIEventDisposition(
  eventId: string,
  disposition: { disposition: 'accepted' | 'edited' | 'rejected'; disposition_notes?: string }
): Promise<AIEvent> {
  const response = await api.patch<AIEvent>(
    `/ai/events/${eventId}/disposition`,
    disposition
  );
  return response.data;
}

export async function getRiskItemAIEvents(
  projectId: string,
  riskItemId: string
): Promise<AIEvent[]> {
  const response = await api.get<AIEvent[]>(
    `/projects/${projectId}/risk-items/${riskItemId}/ai/events`
  );
  return response.data;
}

// Handoff Actions
export interface DesignHandoffResponse {
  created_artifact: any;
  trace_link: TraceLink;
  message: string;
}

export async function handoffControlToDesign(
  projectId: string,
  riskItemId: string,
  controlId: string,
  payload: {
    target_type: 'design_input' | 'design_output' | 'vv_test';
    name?: string;
    description?: string;
    test_method?: string;
    acceptance_criteria?: string;
    design_output_id?: string;
  },
  idempotencyKey?: string
): Promise<DesignHandoffResponse> {
  const headers: Record<string, string> = {};
  if (idempotencyKey) {
    headers['Idempotency-Key'] = idempotencyKey;
  }
  const response = await api.post<DesignHandoffResponse>(
    `/projects/${projectId}/risk-items/${riskItemId}/controls/${controlId}/handoff/design`,
    payload,
    { headers }
  );
  return response.data;
}

export interface CAPAHandoffResponse {
  created_artifact: any;
  trace_link: TraceLink;
  message: string;
}

export async function handoffRiskToCAPA(
  projectId: string,
  riskItemId: string,
  payload: {
    title?: string;
    root_cause?: string;
    capa_plan?: string;
    effectiveness_check?: string;
  },
  idempotencyKey?: string
): Promise<CAPAHandoffResponse> {
  const headers: Record<string, string> = {};
  if (idempotencyKey) {
    headers['Idempotency-Key'] = idempotencyKey;
  }
  const response = await api.post<CAPAHandoffResponse>(
    `/projects/${projectId}/risk-items/${riskItemId}/handoff/capa`,
    payload,
    { headers }
  );
  return response.data;
}

export interface ChangeHandoffResponse {
  created_artifact: any;
  trace_link: TraceLink;
  message: string;
}

export async function handoffRiskVersionToChange(
  projectId: string,
  riskItemId: string,
  payload: {
    version_id?: string;
    title?: string;
    change_summary?: string;
  },
  idempotencyKey?: string
): Promise<ChangeHandoffResponse> {
  const headers: Record<string, string> = {};
  if (idempotencyKey) {
    headers['Idempotency-Key'] = idempotencyKey;
  }
  const response = await api.post<ChangeHandoffResponse>(
    `/projects/${projectId}/risk-items/${riskItemId}/handoff/change`,
    payload,
    { headers }
  );
  return response.data;
}

