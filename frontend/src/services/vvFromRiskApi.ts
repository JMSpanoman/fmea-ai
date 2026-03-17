/**
 * API for risk-based V&V generation (from FMEA/risk row).
 * POST /ai/vv/generate-from-risk, POST /ai/vv/save-from-risk
 */
import api from '../axios';
import type {
  VVFromRiskGenerateRequest,
  VVFromRiskGenerateResponse,
  VVFromRiskCalculationItem,
  VVFromRiskTraceability,
} from '../types';

export async function generateVVFromRisk(
  payload: VVFromRiskGenerateRequest
): Promise<VVFromRiskGenerateResponse> {
  const { data } = await api.post<VVFromRiskGenerateResponse>(
    '/ai/vv/generate-from-risk',
    payload
  );
  return data;
}

export interface SaveVVFromRiskPayload {
  project_id: string;
  fmea_row_id?: string | null;
  risk_item_id?: string | null;
  verification_test_name: string;
  verification_objective: string;
  verification_method: string;
  validation_test_name?: string | null;
  validation_objective?: string | null;
  validation_method_or_scenario?: string | null;
  validation_scenario?: string | null;
  acceptance_criteria: string[];
  calculations: VVFromRiskCalculationItem[];
  worst_case_conditions: string[];
  sample_size_rationale?: string | null;
  traceability: VVFromRiskTraceability;
}

export interface SaveVVFromRiskResponse {
  id: string;
  project_id: string;
  created_at?: string | null;
}

export async function saveVVFromRisk(
  payload: SaveVVFromRiskPayload
): Promise<SaveVVFromRiskResponse> {
  const { data } = await api.post<SaveVVFromRiskResponse>(
    '/ai/vv/save-from-risk',
    payload,
    { headers: { 'Content-Type': 'application/json' } }
  );
  return data;
}
