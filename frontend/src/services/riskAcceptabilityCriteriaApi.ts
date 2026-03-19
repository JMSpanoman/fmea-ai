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
  section_metadata?: Record<string, {
    source_type?: string;
    requires_human_review?: boolean;
    completeness?: 'complete' | 'partial' | 'missing';
    approved_by?: string | null;
    approved_at?: string | null;
    last_updated_at?: string | null;
  }>;
  readiness?: {
    completeness_percentage?: number;
    approved_content_percentage?: number;
    sections_requiring_manual_review?: number;
    blocked_approval_reasons?: string[];
  };
  editable_defaults?: Record<string, {
    current_value?: string;
    source_type?: string;
    last_edited_by?: string | null;
    last_edited_at?: string | null;
    default_value?: string;
  }>;
  manual_review_items?: Array<{
    id?: string;
    message?: string;
    section?: string;
    issue?: string;
    why_it_matters?: string;
    where_to_fix?: string;
    effect_on_approval_readiness?: string;
  }>;
  source_metadata?: Record<string, string>;
  sections?: Record<string, {
    key: string;
    value: unknown;
    source_type: 'system_default' | 'org_default' | 'project_override' | 'user_edited' | string;
    is_user_edited: boolean;
    approved: boolean;
    version: number;
    last_edited_by?: string | null;
    last_edited_at?: string | null;
  }>;
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

  generateReport: (
    projectId: string,
    useAi = false,
    regenerateUsingDefaults = false,
    forceRegenerate = false,
  ): Promise<RiskAcceptabilityReportResponse> => {
    return api.post(generateUrl(projectId), null, { params: { use_ai: useAi, regenerate_using_defaults: regenerateUsingDefaults, force_regenerate: forceRegenerate } }).then((r) => r.data);
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
      terminology_overrides?: Record<string, string>;
      severity_rationale?: string;
      probability_rationale?: string;
      matrix_rationale?: string;
      decision_rules_rationale?: string;
      overall_residual_risk_methods?: string[];
    }
  ) => api.patch(overrideUrl(projectId), body).then((r) => r.data),

  updateWorkflowStatus: (
    projectId: string,
    reportId: string,
    body: { status: string; approval_notes?: string; rejection_reason?: string }
  ) => api.post(`/projects/${projectId}/risk-acceptability-criteria/reports/${reportId}/status`, body).then((r) => r.data),

  addReviewComment: (
    projectId: string,
    reportId: string,
    body: { section_key: string; comment: string }
  ) => api.post(`/projects/${projectId}/risk-acceptability-criteria/reports/${reportId}/comments`, body).then((r) => r.data),

  updateEditableDefaults: (
    projectId: string,
    reportId: string,
    body: {
      decision_rule_wording?: string;
      alarp_terminology?: string;
      severity_rationale?: string;
      probability_rationale?: string;
      matrix_rationale?: string;
      decision_rules_rationale?: string;
      reset_to_default?: string[];
    }
  ) => api.patch(`/projects/${projectId}/risk-acceptability-criteria/reports/${reportId}/editable-defaults`, body).then((r) => r.data),

  updateSection: (
    projectId: string,
    reportId: string,
    sectionKey: string,
    value: unknown,
  ) => api.patch(`/projects/${projectId}/risk-acceptability-criteria/reports/${reportId}/sections/${sectionKey}`, { value }).then((r) => r.data),

  approveSection: (
    projectId: string,
    reportId: string,
    sectionKey: string,
    approved = true,
  ) => api.post(`/projects/${projectId}/risk-acceptability-criteria/reports/${reportId}/sections/${sectionKey}/approve`, { approved }).then((r) => r.data),

  approveAllSections: (
    projectId: string,
    reportId: string,
  ) => api.post(`/projects/${projectId}/risk-acceptability-criteria/reports/${reportId}/approve-all-sections`).then((r) => r.data),

  resetSectionToDefault: (
    projectId: string,
    reportId: string,
    sectionKey: string,
  ) => api.post(`/projects/${projectId}/risk-acceptability-criteria/reports/${reportId}/sections/${sectionKey}/reset-default`).then((r) => r.data),

  resetOverride: (projectId: string) =>
    api.post(`/projects/${projectId}/risk-acceptability-criteria/override/reset`).then((r) => r.data),

  compareOrgDefault: (projectId: string) =>
    api.get(`/projects/${projectId}/risk-acceptability-criteria/compare-org-default`).then((r) => r.data),

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
