/**
 * Risk Acceptability Criteria report and configuration API (ISO 14971).
 */
import api from '../axios';

export interface RiskAcceptabilityReportResponse {
  id?: string | null;
  project_id: string;
  version: number;
  status: string;
  title?: string | null;
  report: RiskAcceptabilityReport;
  rendered_html?: string | null;
  generated_at?: string | null;
}

export interface RiskAcceptabilityReport {
  document_header?: Record<string, unknown>;
  purpose?: { text?: string; source_type?: string };
  scope?: { text?: string; source_type?: string };
  regulatory_basis?: { text?: string; source_type?: string };
  definitions?: { items?: Record<string, string>; source_type?: string };
  severity_scale?: { scale?: Array<{ level?: number; label?: string; definition?: string }>; source_type?: string; label?: string };
  probability_scale?: { scale?: Array<{ level?: number; label?: string; definition?: string }>; source_type?: string; label?: string };
  risk_matrix?: { matrix?: unknown; description?: string; source_type?: string; label?: string };
  decision_rules?: { text?: string; source_type?: string };
  residual_risk_rules?: { text?: string; source_type?: string };
  benefit_risk_triggers?: { text?: string; source_type?: string };
  control_effectiveness_expectations?: { text?: string; source_type?: string };
  overall_residual_risk?: { text?: string; source_type?: string; requires_human_review?: boolean };
  roles_and_responsibilities?: { roles?: Array<{ role?: string; name?: string; responsibility?: string }>; source_type?: string };
  review_and_approval?: Record<string, unknown>;
  traceability_references?: Record<string, { id?: string; status?: string }>;
  ai_transparency?: { text?: string; source_type?: string };
  manual_review_items?: Array<{ id?: string; message?: string; section?: string }>;
  source_metadata?: Record<string, string>;
}

export interface MergedCriteriaResponse {
  criteria: {
    severity_scale?: unknown;
    probability_scale?: unknown;
    risk_matrix?: unknown;
    decision_rules?: string;
  };
  source_metadata?: Record<string, string>;
}

const reportUrl = (projectId: string) => `/projects/${projectId}/risk-acceptability-criteria/report`;
const mergedUrl = (projectId: string) => `/projects/${projectId}/risk-acceptability-criteria/merged`;
const overrideUrl = (projectId: string) => `/projects/${projectId}/risk-acceptability-criteria/override`;
const generateUrl = (projectId: string) => `/projects/${projectId}/risk-acceptability-criteria/generate`;

export const riskAcceptabilityCriteriaApi = {
  getReport: (projectId: string, version?: number): Promise<RiskAcceptabilityReportResponse> => {
    const params = version != null ? { version } : {};
    return api.get(reportUrl(projectId), { params }).then((r) => r.data);
  },

  generateReport: (projectId: string, useAi = false): Promise<RiskAcceptabilityReportResponse> => {
    return api.post(generateUrl(projectId), null, { params: { use_ai: useAi } }).then((r) => r.data);
  },

  getMergedCriteria: (projectId: string): Promise<MergedCriteriaResponse> => {
    return api.get(mergedUrl(projectId)).then((r) => r.data);
  },

  getOverride: (projectId: string) =>
    api.get(overrideUrl(projectId)).then((r) => r.data),

  updateOverride: (
    projectId: string,
    body: {
      severity_scale?: Array<Record<string, unknown>>;
      probability_scale?: Array<Record<string, unknown>>;
      risk_matrix?: Record<string, unknown>;
      decision_rules?: string;
    }
  ) => api.patch(overrideUrl(projectId), body).then((r) => r.data),

  getOrgConfig: () =>
    api.get('/risk-acceptability-criteria/org-config').then((r) => r.data),

  updateOrgConfig: (body: {
    severity_scale?: Array<Record<string, unknown>>;
    probability_scale?: Array<Record<string, unknown>>;
    risk_matrix?: Record<string, unknown>;
    decision_rules?: string;
    terminology_overrides?: Record<string, string>;
  }) => api.patch('/risk-acceptability-criteria/org-config', body).then((r) => r.data),
};
