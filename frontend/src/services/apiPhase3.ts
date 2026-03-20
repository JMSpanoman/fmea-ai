// Phase 3 API Service
import {
  Document, DocumentVersion, TrainingRecord, ChangeControl, Audit, Supplier, SupplierEvaluation,
  NCR, Complaint, Equipment, CalibrationRecord, QualityEvent, Approval,
  DocumentDraftRequest, DocumentDraftResponse, AuditPrepareRequest, AuditPrepareResponse,
  ChangeControlImpactRequest, ChangeControlImpactResponse, ComplaintInvestigateRequest,
  ComplaintInvestigateResponse, NCRAnalyzeRequest, NCRAnalyzeResponse,
  SupplierRiskRequest, SupplierRiskResponse
} from '../types';

import api from '../axios';

function notifyProjectDocumentsChanged(projectId: string) {
  if (typeof window === 'undefined') return;
  try {
    window.dispatchEvent(new CustomEvent('project-documents-changed', { detail: { projectId } }));
  } catch {
    // ignore
  }
}

const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const method = (options.method || 'GET').toUpperCase();
  const rawBody = options.body;
  const data =
    typeof rawBody === 'string' && rawBody.length > 0 ? JSON.parse(rawBody) : undefined;

  try {
    const res = await api.request<T>({
      url: endpoint,
      method: method as any,
      data,
    });
    return res.data;
  } catch (err: any) {
    const detail =
      err?.response?.data?.detail ||
      err?.message ||
      'Request failed';
    throw new Error(detail);
  }
};

// Document Control API
export const documentsApi = {
  getAll: (projectId: string): Promise<Document[]> =>
    apiRequest<Document[]>(`/projects/${projectId}/documents`),
  getById: (projectId: string, documentId: string): Promise<Document> =>
    apiRequest<Document>(`/projects/${projectId}/documents/${documentId}`),
  getGuidanceRegistry: (): Promise<Record<string, { purpose_text: string; population_text: string; ai_available: boolean; ai_button_text?: string }>> =>
    apiRequest<Record<string, { purpose_text: string; population_text: string; ai_available: boolean; ai_button_text?: string }>>(
      '/documents/guidance'
    ),
  generateAiSampleForType: (projectId: string, documentType: string): Promise<Document> =>
    apiRequest<Document>(`/projects/${projectId}/documents/${documentType}/ai-sample`, { method: 'POST' }),
  generateAiExampleForType: (projectId: string, documentType: string): Promise<Document> =>
    apiRequest<Document>(`/projects/${projectId}/documents/${documentType}/generate-ai`, { method: 'POST' }),
  generateWithAiForType: (projectId: string, documentType: string): Promise<Document> =>
    apiRequest<Document>(`/projects/${projectId}/documents/${documentType}/generate-with-ai`, { method: 'POST' }),
  create: async (projectId: string, document: Partial<Document>): Promise<Document> => {
    const created = await apiRequest<Document>(`/projects/${projectId}/documents`, {
      method: 'POST',
      body: JSON.stringify(document),
    });
    notifyProjectDocumentsChanged(projectId);
    return created;
  },
  update: async (projectId: string, documentId: string, document: Partial<Document>): Promise<Document> => {
    const updated = await apiRequest<Document>(`/projects/${projectId}/documents/${documentId}`, {
      method: 'PUT',
      body: JSON.stringify(document),
    });
    notifyProjectDocumentsChanged(projectId);
    return updated;
  },
  approve: async (projectId: string, documentId: string): Promise<Document> => {
    const approved = await apiRequest<Document>(`/projects/${projectId}/documents/${documentId}/approve`, {
      method: 'POST',
    });
    notifyProjectDocumentsChanged(projectId);
    return approved;
  },
  getVersions: (projectId: string, documentId: string): Promise<DocumentVersion[]> =>
    apiRequest<DocumentVersion[]>(`/projects/${projectId}/documents/${documentId}/versions`),
  /** Full version payload including `content` (use for diff / offline review when list omits large HTML). */
  getVersion: (projectId: string, documentId: string, versionNo: number): Promise<DocumentVersion> =>
    apiRequest<DocumentVersion>(`/projects/${projectId}/documents/${documentId}/versions/${versionNo}`),
};

// Training API
export const trainingApi = {
  getUserTraining: (userId: string): Promise<TrainingRecord[]> =>
    apiRequest<TrainingRecord[]>(`/users/${userId}/training`),
  assign: (userId: string, user_id: string, document_id: string): Promise<TrainingRecord> =>
    apiRequest<TrainingRecord>(`/users/${userId}/training/assign`, {
      method: 'POST',
      body: JSON.stringify({ user_id, document_id }),
    }),
  complete: (userId: string, training_record_id: string): Promise<TrainingRecord> =>
    apiRequest<TrainingRecord>(`/users/${userId}/training/complete`, {
      method: 'POST',
      body: JSON.stringify({ training_record_id }),
    }),
};

// Change Control API
export const changeControlsApi = {
  getAll: (projectId: string): Promise<ChangeControl[]> =>
    apiRequest<ChangeControl[]>(`/projects/${projectId}/changes`),
  create: (projectId: string, changeControl: Partial<ChangeControl>): Promise<ChangeControl> =>
    apiRequest<ChangeControl>(`/projects/${projectId}/changes`, {
      method: 'POST',
      body: JSON.stringify(changeControl),
    }),
  update: (projectId: string, changeId: string, changeControl: Partial<ChangeControl>): Promise<ChangeControl> =>
    apiRequest<ChangeControl>(`/projects/${projectId}/changes/${changeId}`, {
      method: 'PUT',
      body: JSON.stringify(changeControl),
    }),
  approve: (projectId: string, changeId: string): Promise<ChangeControl> =>
    apiRequest<ChangeControl>(`/projects/${projectId}/changes/${changeId}/approve`, {
      method: 'POST',
    }),
};

// Audit API
export const auditsApi = {
  getAll: (projectId: string): Promise<Audit[]> =>
    apiRequest<Audit[]>(`/projects/${projectId}/audits`),
  create: (projectId: string, audit: Partial<Audit>): Promise<Audit> =>
    apiRequest<Audit>(`/projects/${projectId}/audits`, {
      method: 'POST',
      body: JSON.stringify(audit),
    }),
  addFinding: (projectId: string, auditId: string, finding: { finding: string; severity?: string; category?: string }): Promise<Audit> =>
    apiRequest<Audit>(`/projects/${projectId}/audits/${auditId}/finding`, {
      method: 'POST',
      body: JSON.stringify(finding),
    }),
  close: (projectId: string, auditId: string): Promise<Audit> =>
    apiRequest<Audit>(`/projects/${projectId}/audits/${auditId}/close`, {
      method: 'POST',
    }),
};

// Supplier API
export const suppliersApi = {
  getAll: (projectId: string): Promise<Supplier[]> =>
    apiRequest<Supplier[]>(`/projects/${projectId}/suppliers`),
  create: (projectId: string, supplier: Partial<Supplier>): Promise<Supplier> =>
    apiRequest<Supplier>(`/projects/${projectId}/suppliers`, {
      method: 'POST',
      body: JSON.stringify(supplier),
    }),
  evaluate: (projectId: string, supplierId: string, evaluation: Partial<SupplierEvaluation>): Promise<SupplierEvaluation> =>
    apiRequest<SupplierEvaluation>(`/projects/${projectId}/suppliers/${supplierId}/evaluate`, {
      method: 'POST',
      body: JSON.stringify(evaluation),
    }),
};

// NCR API
export const ncrsApi = {
  getAll: (projectId: string): Promise<NCR[]> =>
    apiRequest<NCR[]>(`/projects/${projectId}/ncrs`),
  create: (projectId: string, ncr: Partial<NCR>): Promise<NCR> =>
    apiRequest<NCR>(`/projects/${projectId}/ncrs`, {
      method: 'POST',
      body: JSON.stringify(ncr),
    }),
  close: (projectId: string, ncrId: string): Promise<NCR> =>
    apiRequest<NCR>(`/projects/${projectId}/ncrs/${ncrId}/close`, {
      method: 'POST',
    }),
};

// Complaint API
export const complaintsApi = {
  getAll: (projectId: string): Promise<Complaint[]> =>
    apiRequest<Complaint[]>(`/projects/${projectId}/complaints`),
  create: (projectId: string, complaint: Partial<Complaint>): Promise<Complaint> =>
    apiRequest<Complaint>(`/projects/${projectId}/complaints`, {
      method: 'POST',
      body: JSON.stringify(complaint),
    }),
  investigate: (projectId: string, complaintId: string, investigation: string): Promise<Complaint> =>
    apiRequest<Complaint>(`/projects/${projectId}/complaints/${complaintId}/investigate`, {
      method: 'POST',
      body: JSON.stringify({ investigation }),
    }),
};

// Equipment API
export const equipmentApi = {
  getAll: (projectId: string): Promise<Equipment[]> =>
    apiRequest<Equipment[]>(`/projects/${projectId}/equipment`),
  create: (projectId: string, equipment: Partial<Equipment>): Promise<Equipment> =>
    apiRequest<Equipment>(`/projects/${projectId}/equipment`, {
      method: 'POST',
      body: JSON.stringify(equipment),
    }),
  calibrate: (projectId: string, equipmentId: string, calibration: Partial<CalibrationRecord>): Promise<CalibrationRecord> =>
    apiRequest<CalibrationRecord>(`/projects/${projectId}/equipment/${equipmentId}/calibrate`, {
      method: 'POST',
      body: JSON.stringify(calibration),
    }),
  getCalibrationRecords: (projectId: string, equipmentId: string): Promise<CalibrationRecord[]> =>
    apiRequest<CalibrationRecord[]>(`/projects/${projectId}/equipment/${equipmentId}/calibration`),
};

// Quality Events API
export const qualityEventsApi = {
  getAll: (projectId: string): Promise<QualityEvent[]> =>
    apiRequest<QualityEvent[]>(`/projects/${projectId}/events`),
  create: (projectId: string, event: Partial<QualityEvent>): Promise<QualityEvent> =>
    apiRequest<QualityEvent>(`/projects/${projectId}/events`, {
      method: 'POST',
      body: JSON.stringify(event),
    }),
  linkRisks: (projectId: string, eventId: string, riskIds: string[]): Promise<QualityEvent> =>
    apiRequest<QualityEvent>(`/projects/${projectId}/events/${eventId}/link-risks`, {
      method: 'POST',
      body: JSON.stringify({ risk_ids: riskIds }),
    }),
};

// Approvals API
export const approvalsApi = {
  create: (approval: Partial<Approval>): Promise<Approval> =>
    apiRequest<Approval>('/approvals', {
      method: 'POST',
      body: JSON.stringify(approval),
    }),
  getByArtifact: (artifactType: string, artifactId: string): Promise<Approval[]> =>
    apiRequest<Approval[]>(`/approvals/${artifactType}/${artifactId}`),
};

// Phase 3 AI API
export const aiPhase3Api = {
  draftDocument: (request: DocumentDraftRequest): Promise<DocumentDraftResponse> =>
    apiRequest<DocumentDraftResponse>('/ai/documents/draft', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
  summarizeDocument: (documentId: string): Promise<{ summary: string; ai_metadata?: Record<string, any> }> =>
    apiRequest(`/ai/documents/summarize`, {
      method: 'POST',
      body: JSON.stringify({ document_id: documentId }),
    }),
  extractRequirements: (documentId: string): Promise<{ requirements: string[]; ai_metadata?: Record<string, any> }> =>
    apiRequest(`/ai/documents/extract-requirements`, {
      method: 'POST',
      body: JSON.stringify({ document_id: documentId }),
    }),
  prepareAudit: (request: AuditPrepareRequest): Promise<AuditPrepareResponse> =>
    apiRequest<AuditPrepareResponse>('/ai/audits/prepare', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
  analyzeChangeImpact: (request: ChangeControlImpactRequest): Promise<ChangeControlImpactResponse> =>
    apiRequest<ChangeControlImpactResponse>('/ai/changes/impact', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
  investigateComplaint: (request: ComplaintInvestigateRequest): Promise<ComplaintInvestigateResponse> =>
    apiRequest<ComplaintInvestigateResponse>('/ai/complaints/investigate', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
  analyzeNCR: (request: NCRAnalyzeRequest): Promise<NCRAnalyzeResponse> =>
    apiRequest<NCRAnalyzeResponse>('/ai/ncrs/analyze', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
  assessSupplierRisk: (request: SupplierRiskRequest): Promise<SupplierRiskResponse> =>
    apiRequest<SupplierRiskResponse>('/ai/suppliers/risk', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
  generateValidation: (systemName: string, moduleName?: string): Promise<any> =>
    apiRequest('/ai/validation/generate', {
      method: 'POST',
      body: JSON.stringify({ system_name: systemName, module_name: moduleName }),
    }),
};

