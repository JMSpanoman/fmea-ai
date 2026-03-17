/**
 * API client for Risk Knowledge Base (Hazard, Harm, Risk Control, Verification libraries).
 */
import api from '../axios';

const BASE = '/risk-knowledge-base';

// ----- Types -----
export interface HazardLibraryRecord {
  id: string;
  code?: string | null;
  name: string;
  description?: string | null;
  category?: string | null;
  source_standard?: string | null;
  is_active: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface HazardLibraryCreate {
  code?: string;
  name: string;
  description?: string;
  category?: string;
  source_standard?: string;
  is_active?: boolean;
}

export interface HazardLibraryUpdate {
  code?: string;
  name?: string;
  description?: string;
  category?: string;
  source_standard?: string;
  is_active?: boolean;
}

export interface HarmLibraryRecord {
  id: string;
  harm_id?: string | null;
  harm_name: string;
  description?: string | null;
  severity_guidance?: string | null;
  clinical_examples?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface HarmLibraryCreate {
  harm_id?: string;
  harm_name: string;
  description?: string;
  severity_guidance?: string;
  clinical_examples?: string;
}

export interface HarmLibraryUpdate {
  harm_id?: string;
  harm_name?: string;
  description?: string;
  severity_guidance?: string;
  clinical_examples?: string;
}

export interface RiskControlLibraryRecord {
  id: string;
  control_id?: string | null;
  control_name: string;
  control_type: string;
  description?: string | null;
  example_application?: string | null;
  typical_verification_method?: string | null;
  related_standards?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface RiskControlLibraryCreate {
  control_id?: string;
  control_name: string;
  control_type: string;
  description?: string;
  example_application?: string;
  typical_verification_method?: string;
  related_standards?: string;
}

export interface RiskControlLibraryUpdate {
  control_id?: string;
  control_name?: string;
  control_type?: string;
  description?: string;
  example_application?: string;
  typical_verification_method?: string;
  related_standards?: string;
}

export interface VerificationLibraryRecord {
  id: string;
  verification_id?: string | null;
  verification_method: string;
  description?: string | null;
  applicable_control_types?: string | null;
  standard_reference?: string | null;
  typical_test_output?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface VerificationLibraryCreate {
  verification_id?: string;
  verification_method: string;
  description?: string;
  applicable_control_types?: string;
  standard_reference?: string;
  typical_test_output?: string;
}

export interface VerificationLibraryUpdate {
  verification_id?: string;
  verification_method?: string;
  description?: string;
  applicable_control_types?: string;
  standard_reference?: string;
  typical_test_output?: string;
}

// ----- Hazard Library -----
export const hazardLibraryApi = {
  list: (params?: { skip?: number; limit?: number; is_active?: boolean; category?: string; search?: string }) =>
    api.get<HazardLibraryRecord[]>(`${BASE}/hazards`, { params: params || {} }).then((r) => r.data),
  get: (id: string) => api.get<HazardLibraryRecord>(`${BASE}/hazards/${id}`).then((r) => r.data),
  create: (body: HazardLibraryCreate) =>
    api.post<HazardLibraryRecord>(`${BASE}/hazards`, body).then((r) => r.data),
  update: (id: string, body: HazardLibraryUpdate) =>
    api.put<HazardLibraryRecord>(`${BASE}/hazards/${id}`, body).then((r) => r.data),
  delete: (id: string) => api.delete(`${BASE}/hazards/${id}`),
};

// ----- Harm Library -----
export const harmLibraryApi = {
  list: (params?: { skip?: number; limit?: number; search?: string }) =>
    api.get<HarmLibraryRecord[]>(`${BASE}/harms`, { params: params || {} }).then((r) => r.data),
  get: (id: string) => api.get<HarmLibraryRecord>(`${BASE}/harms/${id}`).then((r) => r.data),
  create: (body: HarmLibraryCreate) =>
    api.post<HarmLibraryRecord>(`${BASE}/harms`, body).then((r) => r.data),
  update: (id: string, body: HarmLibraryUpdate) =>
    api.put<HarmLibraryRecord>(`${BASE}/harms/${id}`, body).then((r) => r.data),
  delete: (id: string) => api.delete(`${BASE}/harms/${id}`),
};

// ----- Risk Control Library -----
export const riskControlLibraryApi = {
  list: (params?: { skip?: number; limit?: number; control_type?: string; search?: string }) =>
    api
      .get<RiskControlLibraryRecord[]>(`${BASE}/risk-controls`, { params: params || {} })
      .then((r) => r.data),
  get: (id: string) =>
    api.get<RiskControlLibraryRecord>(`${BASE}/risk-controls/${id}`).then((r) => r.data),
  create: (body: RiskControlLibraryCreate) =>
    api.post<RiskControlLibraryRecord>(`${BASE}/risk-controls`, body).then((r) => r.data),
  update: (id: string, body: RiskControlLibraryUpdate) =>
    api.put<RiskControlLibraryRecord>(`${BASE}/risk-controls/${id}`, body).then((r) => r.data),
  delete: (id: string) => api.delete(`${BASE}/risk-controls/${id}`),
};

// ----- Verification Library -----
export const verificationLibraryApi = {
  list: (params?: { skip?: number; limit?: number; search?: string }) =>
    api
      .get<VerificationLibraryRecord[]>(`${BASE}/verifications`, { params: params || {} })
      .then((r) => r.data),
  get: (id: string) =>
    api.get<VerificationLibraryRecord>(`${BASE}/verifications/${id}`).then((r) => r.data),
  create: (body: VerificationLibraryCreate) =>
    api.post<VerificationLibraryRecord>(`${BASE}/verifications`, body).then((r) => r.data),
  update: (id: string, body: VerificationLibraryUpdate) =>
    api.put<VerificationLibraryRecord>(`${BASE}/verifications/${id}`, body).then((r) => r.data),
  delete: (id: string) => api.delete(`${BASE}/verifications/${id}`),
};
