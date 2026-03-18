/**
 * Phase 4: Structured risk outputs from project_risk_items.
 */
import api from '../axios';

function base(projectId: string) {
  return `/projects/${projectId}/risk-outputs`;
}

export interface FmeaRow {
  id: string;
  row_number: number;
  component: string;
  failure_mode: string;
  effect: string;
  cause: string;
  severity: number | null;
  probability: number | null;
  detectability: number | null;
  risk_score: number | null;
  risk_control: string;
  verification: string;
  residual_risk: string;
}

export interface HazardAnalysisRow {
  id: string;
  row_number: number;
  hazard: string;
  hazardous_situation: string;
  harm: string;
  sequence_of_events: string;
  severity: number | null;
  probability: number | null;
}

export interface RiskAnalysisRow {
  id: string;
  row_number: number;
  device: string;
  component: string;
  failure_mode: string;
  hazard: string;
  harm: string;
  severity: number | null;
  probability: number | null;
  detectability: number | null;
  risk_score: number | null;
  risk_acceptability: string;
  risk_controls_summary: string;
  status: string;
}

export interface RiskControlTraceabilityRow {
  project_risk_item_id: string;
  project_risk_control_id: string;
  risk_item: string;
  hazard: string;
  control: string;
  implementation_reference: string;
  verification: string;
  evidence_reference: string;
}

export interface VerificationTraceabilityRow {
  project_risk_control_id: string;
  project_verification_id: string;
  component: string;
  control_text: string;
  verification_text: string;
  verification_library_id: string | null;
  evidence_reference: string;
  status: string;
}

export interface ResidualRiskRow {
  id: string;
  row_number: number;
  risk_item: string;
  initial_risk: string;
  controls_applied: string;
  residual_severity: number | null;
  residual_probability: number | null;
  residual_risk_score: number | null;
  acceptable: string;
}

export interface RiskManagementReportDraft {
  sections: {
    introduction: string;
    hazard_analysis_summary: string;
    risk_analysis_summary: string;
    risk_controls_summary: string;
    verification_summary: string;
    residual_risk_summary: string;
    traceability: string;
  };
  full_draft: string;
  stats: {
    risk_items_count: number;
    hazard_rows_count: number;
    fmea_rows_count: number;
    residual_rows_count: number;
  };
}

export const projectRiskOutputsApi = {
  getFmeaTable: (projectId: string) =>
    api.get<{ rows: FmeaRow[] }>(`${base(projectId)}/fmea-table`).then((r) => r.data.rows),
  getHazardAnalysisTable: (projectId: string) =>
    api.get<{ rows: HazardAnalysisRow[] }>(`${base(projectId)}/hazard-analysis-table`).then((r) => r.data.rows),
  getRiskAnalysisTable: (projectId: string) =>
    api.get<{ rows: RiskAnalysisRow[] }>(`${base(projectId)}/risk-analysis-table`).then((r) => r.data.rows),
  getRiskControlTraceabilityTable: (projectId: string) =>
    api.get<{ rows: RiskControlTraceabilityRow[] }>(`${base(projectId)}/risk-control-traceability-table`).then((r) => r.data.rows),
  getVerificationTraceabilityTable: (projectId: string) =>
    api.get<{ rows: VerificationTraceabilityRow[] }>(`${base(projectId)}/verification-traceability-table`).then((r) => r.data.rows),
  getResidualRiskEvaluationTable: (projectId: string) =>
    api.get<{ rows: ResidualRiskRow[] }>(`${base(projectId)}/residual-risk-evaluation-table`).then((r) => r.data.rows),
  getRiskManagementReportDraft: (projectId: string) =>
    api.get<RiskManagementReportDraft>(`${base(projectId)}/risk-management-report-draft`).then((r) => r.data),
};
