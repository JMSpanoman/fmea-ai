/**
 * Deterministic risk acceptability rule engine API (FMEA row evaluation).
 */
import api from '../axios';

export interface ProjectRiskCriteria {
  id: string;
  project_id: string;
  version: number;
  status: string;
  evaluation_method: string;
  severity_scale?: unknown;
  probability_scale?: unknown;
  detection_scale?: unknown;
  risk_matrix?: Record<string, Record<string, string>>;
  score_thresholds?: Record<string, unknown>;
  special_rules?: Record<string, unknown>;
  approval_metadata?: Record<string, unknown> | null;
  created_at?: string;
  updated_at?: string | null;
}

export interface RuleEvaluationAudit {
  id: string;
  fmea_row_id: string;
  project_id: string;
  criteria_version: number;
  evaluation_type: string;
  inputs_json?: Record<string, unknown>;
  matched_rules_json?: unknown;
  output_json?: Record<string, unknown>;
  decision_path_text?: string | null;
  created_at?: string;
}

export interface GlobalResidualAcceptability {
  ok: boolean;
  overall_acceptable: boolean;
  blockers: string[];
  decision_path: string[];
  matched_rules: string[];
  policy_applied: boolean;
}

export interface GlobalResidualRiskSummary {
  project_id: string;
  criteria_version: number;
  total_rows: number;
  residual_summary: { acceptable: number; alarp: number; unacceptable: number; unknown: number };
  benefit_risk_required_count: number;
  approval_blocked_count: number;
  critical_function_count: number;
  top_unresolved_risks: Array<Record<string, unknown>>;
  global_residual_acceptability: GlobalResidualAcceptability;
}

export const riskRuleEngineApi = {
  listCriteria(projectId: string) {
    return api.get<ProjectRiskCriteria[]>(`/projects/${projectId}/risk-criteria`).then((r) => r.data);
  },

  createCriteria(projectId: string, body: Partial<ProjectRiskCriteria>) {
    return api.post<ProjectRiskCriteria>(`/projects/${projectId}/risk-criteria`, body).then((r) => r.data);
  },

  seedCriteria(projectId: string, template: string = 'iso14971_default_pacemaker') {
    return api
      .post<ProjectRiskCriteria>(`/projects/${projectId}/risk-criteria/seed`, { template })
      .then((r) => r.data);
  },

  updateCriteria(projectId: string, criteriaId: string, body: Partial<ProjectRiskCriteria>) {
    return api
      .put<ProjectRiskCriteria>(`/projects/${projectId}/risk-criteria/${criteriaId}`, body)
      .then((r) => r.data);
  },

  approveCriteria(projectId: string, criteriaId: string, approval_metadata?: Record<string, unknown>) {
    return api
      .post<ProjectRiskCriteria>(`/projects/${projectId}/risk-criteria/${criteriaId}/approve`, {
        approval_metadata: approval_metadata ?? {},
      })
      .then((r) => r.data);
  },

  evaluateInitial(projectId: string, rowId: string, criteriaId?: string) {
    const params = criteriaId ? { criteria_id: criteriaId } : undefined;
    return api
      .post(`/projects/${projectId}/fmea/${rowId}/evaluate-initial`, {}, { params })
      .then((r) => r.data);
  },

  evaluateResidual(projectId: string, rowId: string, criteriaId?: string) {
    const params = criteriaId ? { criteria_id: criteriaId } : undefined;
    return api
      .post(`/projects/${projectId}/fmea/${rowId}/evaluate-residual`, {}, { params })
      .then((r) => r.data);
  },

  reEvaluate(projectId: string, rowId: string, criteriaId?: string) {
    const params = criteriaId ? { criteria_id: criteriaId } : undefined;
    return api
      .post(`/projects/${projectId}/fmea/${rowId}/re-evaluate`, {}, { params })
      .then((r) => r.data);
  },

  evaluateAll(projectId: string, criteriaId?: string) {
    const params = criteriaId ? { criteria_id: criteriaId } : undefined;
    return api.post(`/projects/${projectId}/evaluate-all-risks`, {}, { params }).then((r) => r.data);
  },

  globalSummary(projectId: string) {
    return api
      .get<GlobalResidualRiskSummary>(`/projects/${projectId}/global-residual-risk-summary`)
      .then((r) => r.data);
  },

  listAudit(projectId: string, rowId: string) {
    return api
      .get<RuleEvaluationAudit[]>(`/projects/${projectId}/fmea/${rowId}/rule-audit`)
      .then((r) => r.data);
  },
};
