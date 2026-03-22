import axios from '../axios';

/** Mirrors backend `schemas/capa_workflow` (subset for UI). */
export interface CapaWorkflowPayload {
  trigger: Record<string, unknown>;
  problem: Record<string, unknown>;
  containment: Record<string, unknown>;
  rca: Record<string, unknown>;
  corrective_actions: CorrectiveActionItem[];
  preventive: { items: CorrectiveActionItem[]; scope_expansion_analysis?: string; where_else_evaluation?: string };
  voe_plan: Record<string, unknown>;
  effectiveness_results?: EffectivenessResults | null;
  risk_linkage: Record<string, unknown>;
  regulatory: Record<string, unknown>;
  approvals: ApprovalRecord[];
  closure: Record<string, unknown>;
  ai_review_hooks?: Record<string, unknown>;
}

export interface CorrectiveActionItem {
  id: string;
  description: string;
  owner: string;
  due_date?: string | null;
  status: string;
  action_type?: string | null;
  linked_root_cause_id: string;
}

export interface EffectivenessResults {
  evidence_summary: string;
  result: string;
  date_reviewed?: string | null;
  reviewer: string;
  conclusion?: string | null;
  referenced_evidence_ids: string[];
}

export interface ApprovalRecord {
  id: string;
  kind: string;
  role: string;
  approver_name: string;
  status: string;
  comment?: string;
}

export interface CapaEvidence {
  id: string;
  capa_id: string;
  category: string;
  title: string;
  reference_uri?: string | null;
  notes?: string | null;
  created_at: string;
}

export interface CAPAFull {
  id: string;
  project_id: string;
  created_at: string;
  updated_at?: string | null;
  workflow_state: string;
  root_cause: string;
  capa_plan: string;
  effectiveness_check?: string | null;
  linked_risk_ids?: string[] | null;
  ai_metadata?: Record<string, unknown> | null;
  payload: CapaWorkflowPayload;
  evidences: CapaEvidence[];
}

export async function getCAPA(projectId: string, capaId: string): Promise<CAPAFull> {
  const response = await axios.get<CAPAFull>(`/projects/${projectId}/capas/${capaId}`);
  return response.data;
}

export async function updateCAPA(
  projectId: string,
  capaId: string,
  body: {
    payload?: CapaWorkflowPayload;
    workflow_state?: string;
    root_cause?: string;
    capa_plan?: string;
    effectiveness_check?: string | null;
    linked_risk_ids?: string[] | null;
    ai_metadata?: Record<string, unknown> | null;
  }
): Promise<CAPAFull> {
  const response = await axios.put<CAPAFull>(`/projects/${projectId}/capas/${capaId}`, body);
  return response.data;
}

export async function addCapaEvidence(
  projectId: string,
  capaId: string,
  body: { category: string; title: string; reference_uri?: string; notes?: string }
): Promise<CapaEvidence> {
  const response = await axios.post<CapaEvidence>(
    `/projects/${projectId}/capas/${capaId}/evidences`,
    body
  );
  return response.data;
}

export async function deleteCapaEvidence(projectId: string, capaId: string, evidenceId: string): Promise<void> {
  await axios.delete(`/projects/${projectId}/capas/${capaId}/evidences/${evidenceId}`);
}

export async function getCapaAiReviewHooks(projectId: string): Promise<{ hooks: { id: string; title: string; prompt: string }[] }> {
  const response = await axios.get(`/projects/${projectId}/capas/_meta/ai-review-hooks`);
  return response.data;
}
