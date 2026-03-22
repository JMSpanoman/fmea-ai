/**
 * PMS Plan Generator API (FMEA + MAUDE-like signals + AI).
 * Backend: /pms/* (Pro-gated).
 */
import api, { API_BASE_URL } from '../axios';

export interface PmsMaudeSignal {
  failure_mode: string;
  event_count: number;
  trend: string;
  severity: string;
  source?: string | null;
  notes?: string | null;
  recommended_monitoring_focus?: string | null;
}

export interface PmsPlanSections {
  device_overview: string;
  pms_objectives: string;
  data_sources: string;
  maude_analysis: string;
  risk_mapping: string;
  signal_detection: string;
  pms_activities: string;
  capa_integration: string;
  benefit_risk: string;
  reporting: string;
}

export interface PmsPlanGenerateResponse extends PmsPlanSections {
  generation_id: string;
  project_id: string;
  created_at: string;
  maude_signals: PmsMaudeSignal[];
  fmea_row_count: number;
  model?: string | null;
  ai_generated: boolean;
  summary: string;
  status: string;
  version: number;
  warning?: string | null;
}

export interface PmsPlanHistoryItem {
  id: string;
  project_id: string;
  device_name?: string | null;
  intended_use?: string | null;
  created_at: string;
  input_summary?: string | null;
  summary?: string | null;
  status?: string | null;
  version?: number | null;
  plan: PmsPlanSections;
  maude_signals: PmsMaudeSignal[];
  fmea_row_count?: number | null;
  model?: string | null;
  warning?: string | null;
  ai_generated?: boolean | null;
}

export interface PmsPlanHistoryListResponse {
  project_id: string;
  items: PmsPlanHistoryItem[];
}

export async function generatePmsPlan(body: {
  project_id: string;
  device_name: string;
  intended_use: string;
}): Promise<PmsPlanGenerateResponse> {
  const { data } = await api.post<PmsPlanGenerateResponse>('/pms/generate', body);
  return data;
}

export async function listPmsPlans(projectId: string): Promise<PmsPlanHistoryListResponse> {
  const { data } = await api.get<PmsPlanHistoryListResponse>(`/pms/${encodeURIComponent(projectId)}`);
  return data;
}

export async function getPmsPlan(generationId: string): Promise<PmsPlanHistoryItem> {
  const { data } = await api.get<PmsPlanHistoryItem>(`/pms/plan/${encodeURIComponent(generationId)}`);
  return data;
}

/** Opens printable HTML in a new tab (auth via axios blob). */
export async function openPmsPlanPrintView(generationId: string): Promise<void> {
  const res = await api.get(`/pms/plan/${encodeURIComponent(generationId)}/export/html`, {
    responseType: 'blob',
  });
  const blob = new Blob([res.data], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const w = window.open(url, '_blank', 'noopener,noreferrer');
  if (!w) {
    URL.revokeObjectURL(url);
    throw new Error('Popup blocked — allow popups or use download.');
  }
  w.addEventListener('beforeunload', () => URL.revokeObjectURL(url));
}

/** Raw URL for debugging (no auth). Prefer `openPmsPlanPrintView`. */
export function pmsPlanExportHtmlPath(generationId: string): string {
  return `${API_BASE_URL}/pms/plan/${encodeURIComponent(generationId)}/export/html`;
}
