/**
 * Device-scoped risk outputs and generated documents.
 * Base URL is /api, so paths are relative to that (e.g. /devices/:id/fmea -> /api/devices/:id/fmea).
 */
import api from '../axios';

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

export interface GeneratedDocumentOut {
  id: string;
  device_id: string;
  document_type: string;
  title: string;
  content_json: string | null;
  content_markdown: string | null;
  version: number;
  created_at: string;
  updated_at: string | null;
}

export interface GenerateReportResponse {
  id: string;
  device_id: string;
  document_type: string;
  title: string;
  version: number;
  created_at: string;
}

export const devicesApi = {
  getFmea: (deviceId: string) =>
    api.get<{ rows: FmeaRow[] }>(`/devices/${deviceId}/fmea`).then((r) => r.data.rows),

  getHazardAnalysis: (deviceId: string) =>
    api
      .get<{ rows: HazardAnalysisRow[] }>(`/devices/${deviceId}/hazard-analysis`)
      .then((r) => r.data.rows),

  getRiskTraceability: (deviceId: string) =>
    api
      .get<{ rows: RiskControlTraceabilityRow[] }>(`/devices/${deviceId}/risk-traceability`)
      .then((r) => r.data.rows),

  getResidualRisk: (deviceId: string) =>
    api
      .get<{ rows: ResidualRiskRow[] }>(`/devices/${deviceId}/residual-risk`)
      .then((r) => r.data.rows),

  generateReport: (deviceId: string) =>
    api
      .post<GenerateReportResponse>(`/devices/${deviceId}/generate-report`)
      .then((r) => r.data),

  getGeneratedDocument: (docId: string) =>
    api.get<GeneratedDocumentOut>(`/generated-documents/${docId}`).then((r) => r.data),
};
