// Phase 1 API Service
import { Project, Component, FmeaRow, AIFMEASuggestRequest, AIFMEASuggestResponse, AIConsistencyCheckRequest, AIConsistencyCheckResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Get auth token from localStorage or context
const getAuthToken = (): string | null => {
  // This should be replaced with your actual auth token retrieval
  return localStorage.getItem('auth_token') || null;
};

const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// Projects API
export const projectsApi = {
  getAll: (): Promise<Project[]> => apiRequest<Project[]>('/projects'),
  getById: (id: string): Promise<Project> => apiRequest<Project>(`/projects/${id}`),
  create: (project: { name: string; description?: string }): Promise<Project> =>
    apiRequest<Project>('/projects', { method: 'POST', body: JSON.stringify(project) }),
  delete: (id: string): Promise<void> =>
    apiRequest<void>(`/projects/${id}`, { method: 'DELETE' }),
};

// Components API
export const componentsApi = {
  getByProject: (projectId: string): Promise<Component[]> =>
    apiRequest<Component[]>(`/projects/${projectId}/components`),
  create: (projectId: string, component: { name: string; description?: string }): Promise<Component> =>
    apiRequest<Component>(`/projects/${projectId}/components`, {
      method: 'POST',
      body: JSON.stringify(component),
    }),
};

// FMEA API
export const fmeaApi = {
  getByProject: (projectId: string): Promise<FmeaRow[]> =>
    apiRequest<FmeaRow[]>(`/projects/${projectId}/fmea`),
  create: (projectId: string, fmeaRow: {
    component_id?: string;
    failure_mode?: string;
    effect?: string;
    cause?: string;
    severity?: number;
    probability?: number;
    detection?: number;
    mitigation?: string;
    residual_severity?: number;
    residual_probability?: number;
    residual_detection?: number;
    financial_impact?: number;
    ai_metadata?: Record<string, any>;
  }): Promise<FmeaRow> =>
    apiRequest<FmeaRow>(`/projects/${projectId}/fmea`, {
      method: 'POST',
      body: JSON.stringify(fmeaRow),
    }),
  getById: (projectId: string, id: string): Promise<FmeaRow> =>
    apiRequest<FmeaRow>(`/projects/${projectId}/fmea/${id}`),
  update: (projectId: string, id: string, updates: Partial<FmeaRow>): Promise<FmeaRow> =>
    apiRequest<FmeaRow>(`/projects/${projectId}/fmea/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),
  delete: (projectId: string, id: string): Promise<void> =>
    apiRequest<void>(`/projects/${projectId}/fmea/${id}`, { method: 'DELETE' }),
  getHistory: (projectId: string, id: string): Promise<{ versions: any[] }> =>
    apiRequest<{ versions: any[] }>(`/projects/${projectId}/fmea/${id}/history`),
};

// AI API
export const aiApi = {
  suggest: (request: AIFMEASuggestRequest): Promise<AIFMEASuggestResponse> =>
    apiRequest<AIFMEASuggestResponse>('/ai/fmea/suggest', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
  check: (request: AIConsistencyCheckRequest): Promise<AIConsistencyCheckResponse> =>
    apiRequest<AIConsistencyCheckResponse>('/ai/fmea/check', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
};

// Export API
export const exportApi = {
  csv: (projectId: string): string => `${API_BASE_URL}/projects/${projectId}/export/csv`,
  pdf: (projectId: string): string => `${API_BASE_URL}/projects/${projectId}/export/pdf`,
};

