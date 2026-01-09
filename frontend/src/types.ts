// Phase 1 Types

export interface User {
  id: string; // UUID
  auth0_id?: string;
  email: string;
  created_at: string;
}

export interface Project {
  id: string; // UUID
  user_id: string; // UUID
  name: string;
  description?: string;
  created_at: string;
}

export interface Component {
  id: string; // UUID
  project_id: string; // UUID
  name: string;
  description?: string;
  created_at: string;
}

export interface FmeaRow {
  id: string; // UUID
  project_id: string; // UUID
  component_id?: string; // UUID
  failure_mode?: string;
  effect?: string;
  cause?: string;
  severity?: number;
  probability?: number;
  detection?: number;
  rpn?: number; // Auto-calculated
  mitigation?: string;
  residual_severity?: number;
  residual_probability?: number;
  residual_detection?: number;
  residual_rpn?: number; // Auto-calculated
  financial_impact?: number;
  ai_metadata?: Record<string, any>;
  version: number;
  created_at: string;
  updated_at?: string;
}

export interface FmeaVersion {
  id: string; // UUID
  fmea_row_id: string; // UUID
  version: number;
  diff?: Record<string, { old: any; new: any }>;
  created_at: string;
}

// AI Request/Response Types
export interface AIFMEASuggestRequest {
  component: string;
  failure_mode: string;
  effect: string;
  cause: string;
}

export interface AIFMEASuggestResponse {
  severity: number;
  probability: number;
  detection: number;
  rpn: number;
  mitigation: string;
  financial_impact: number;
  residual_severity: number;
  residual_probability: number;
  residual_detection: number;
  residual_rpn: number;
}

export interface AIConsistencyCheckRequest {
  fmea_row: FmeaRow;
}

export interface AIConsistencyCheckResponse {
  issues: string[];
  recommendations: string[];
}

// Phase 2 Types (if not already present)
export interface DesignInput {
  id: string;
  project_id: string;
  source: "ai" | "user";
  text: string;
  linked_risk_ids?: string[];
  created_at: string;
}

export interface DesignOutput {
  id: string;
  project_id: string;
  source: "ai" | "user";
  text: string;
  linked_input_id?: string;
  created_at: string;
}

export interface VVTest {
  id: string;
  project_id: string;
  design_output_id: string;
  test_method: string;
  acceptance_criteria: string;
  rationale?: string;
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface CAPA {
  id: string;
  project_id: string;
  root_cause: string;
  capa_plan: string;
  effectiveness_check?: string;
  linked_risk_ids?: string[];
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface PMSSignal {
  id: string;
  project_id: string;
  signal_type: string;
  description: string;
  linked_risk_ids?: string[];
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface TraceLink {
  id: string;
  project_id: string;
  from_type: "risk" | "input" | "output" | "test" | "capa" | "pms";
  from_id: string;
  to_type: "risk" | "input" | "output" | "test" | "capa" | "pms";
  to_id: string;
  created_at: string;
}

// Phase 3 Types
export interface Document {
  id: string;
  project_id: string;
  name: string;
  // NOTE: SmartQS now uses project-scoped document types for ISO 14971 workflows.
  // Keep this union broad to match backend values.
  type:
    | "rmp"
    | "rmf"
    | "hazard_analysis"
    | "residual_risk"
    | "risk_controls_doc"
    | "fmea"
    | "traceability_matrix"
    | "dhf"
    | "dmr"
    | "sop"
    | "form"
    | "work_instruction"
    | "record"
    | string;
  content?: string;
  version: number;
  status: "draft" | "in_review" | "approved" | "obsolete";
  ai_metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface DocumentVersion {
  id: string;
  document_id: string;
  version: number;
  content?: string;
  changes?: Record<string, any>;
  created_at: string;
}

export interface TrainingRecord {
  id: string;
  user_id: string;
  document_id: string;
  status: "assigned" | "in_progress" | "complete";
  completed_at?: string;
  created_at: string;
}

export interface ChangeControl {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  reason?: string;
  risk_impact?: Record<string, any>;
  status: "open" | "in_review" | "approved" | "implemented" | "verified" | "closed";
  linked_risk_ids?: string[];
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface Audit {
  id: string;
  project_id: string;
  type: "internal" | "supplier" | "external" | "regulatory";
  scope?: string;
  findings?: Record<string, any>;
  status: string;
  ai_metadata?: Record<string, any>;
  scheduled_date?: string;
  created_at: string;
}

export interface Supplier {
  id: string;
  project_id: string;
  name: string;
  category?: string;
  risk_rating?: number;
  status?: string;
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface SupplierEvaluation {
  id: string;
  supplier_id: string;
  evaluation_text?: string;
  score?: number;
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface NCR {
  id: string;
  project_id: string;
  description: string;
  root_cause?: string;
  containment_action?: string;
  corrective_action?: string;
  status: string;
  linked_risk_ids?: string[];
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface Complaint {
  id: string;
  project_id: string;
  description: string;
  reportability?: "reportable" | "non_reportable";
  investigation?: string;
  linked_risk_ids?: string[];
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface Equipment {
  id: string;
  project_id: string;
  name: string;
  serial_number?: string;
  calibration_due?: string;
  status?: string;
  created_at: string;
}

export interface CalibrationRecord {
  id: string;
  equipment_id: string;
  performed_at: string;
  result?: string;
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface QualityEvent {
  id: string;
  project_id: string;
  event_type: string;
  description: string;
  status: string;
  linked_risk_ids?: string[];
  ai_metadata?: Record<string, any>;
  created_at: string;
}

export interface Approval {
  id: string;
  artifact_type: "document" | "change_control" | "ncr" | "capa" | "audit" | "complaint";
  artifact_id: string;
  approver_id: string;
  status: "pending" | "approved" | "rejected";
  comment?: string;
  timestamp: string;
}

// Phase 3 AI Request/Response Types
export interface DocumentDraftRequest {
  type: string;
  context?: string;
  requirements?: string[];
}

export interface DocumentDraftResponse {
  draft: string;
  ai_metadata?: Record<string, any>;
}

export interface AuditPrepareRequest {
  project_id: string;
  audit_type: string;
}

export interface AuditPrepareResponse {
  checklist: string[];
  gaps: string[];
  risk_areas: string[];
  compliance_warnings: string[];
  ai_metadata?: Record<string, any>;
}

export interface ChangeControlImpactRequest {
  change_control_id: string;
}

export interface ChangeControlImpactResponse {
  affected_risks: string[];
  affected_design_inputs: string[];
  affected_design_outputs: string[];
  affected_vv_tests: string[];
  affected_capas: string[];
  affected_pms_signals: string[];
  ai_metadata?: Record<string, any>;
}

export interface ComplaintInvestigateRequest {
  complaint_id: string;
}

export interface ComplaintInvestigateResponse {
  investigation: string;
  affected_risks: string[];
  reportability_decision: "reportable" | "non_reportable";
  ai_metadata?: Record<string, any>;
}

export interface NCRAnalyzeRequest {
  ncr_id: string;
}

export interface NCRAnalyzeResponse {
  root_cause: string;
  corrective_action: string;
  verification_steps: string[];
  ai_metadata?: Record<string, any>;
}

export interface SupplierRiskRequest {
  supplier_id: string;
}

export interface SupplierRiskResponse {
  risk_rating: number;
  concerns: string[];
  recommended_actions: string[];
  ai_metadata?: Record<string, any>;
}
