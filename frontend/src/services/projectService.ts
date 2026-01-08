// Using authenticated axios client
import api from '../axios';

export interface Project {
  id: string; // UUID
  name: string;
  description: string | null;
  user_id: string;
  
  created_at: string;
  updated_at?: string | null;

  // Backward-compatible optional fields (legacy UI expectations)
  status?: string;
  version_number?: string;
  major_version?: number;
  minor_version?: number;
  patch_version?: number;
  version_status?: string;
  version_label?: string | null;
  change_summary?: string | null;
  change_details?: any | null;
  content_hash?: string | null;
  approval_required?: string;
  approved_by?: string | null;
  approved_at?: string | null;
  version_created_at?: string;
  version_updated_at?: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  version_number?: string;
  major_version?: number;
  minor_version?: number;
  patch_version?: number;
  version_status?: string;
  version_label?: string;
  change_summary?: string;
  change_details?: any;
  content_hash?: string;
  approval_required?: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  status?: string;
  version_number?: string;
  major_version?: number;
  minor_version?: number;
  patch_version?: number;
  version_status?: string;
  version_label?: string;
  change_summary?: string;
  change_details?: any;
  content_hash?: string;
  approval_required?: string;
  approved_by?: string;
  approved_at?: string;
}

class ProjectService {
  async getProjects(): Promise<Project[]> {
    try {
      // Use authenticated axios client - interceptor handles auth header
      const response = await api.get('/projects');
      return response.data;
    } catch (error: any) {
      console.error('[projectService] Error fetching projects:', error);
      if (error.response?.status === 401) {
        throw new Error('You\'re not logged in or your session expired. Please refresh the page.');
      }
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch projects');
    }
  }

  async getProject(id: string): Promise<Project> {
    try {
      // Use authenticated axios client - interceptor handles auth header
      const response = await api.get(`/projects/${id}`);
      return response.data;
    } catch (error: any) {
      console.error(`[projectService] Error fetching project ${id}:`, error);
      if (error.response?.status === 401) {
        throw new Error('You\'re not logged in or your session expired. Please refresh the page.');
      }
      throw new Error(error.response?.data?.detail || error.message || `Failed to fetch project ${id}`);
    }
  }

  async createProject(project: ProjectCreate): Promise<Project> {
    try {
      // Use authenticated axios client - interceptor handles auth header
      const response = await api.post('/projects', project);
      return response.data;
    } catch (error: any) {
      console.error('[projectService] Error creating project:', error);
      if (error.response?.status === 401) {
        throw new Error('You\'re not logged in or your session expired. Please refresh the page.');
      }
      throw new Error(error.response?.data?.detail || error.message || 'Failed to create project');
    }
  }

  async updateProject(id: string, project: ProjectUpdate): Promise<Project> {
    try {
      // Use authenticated axios client - interceptor handles auth header
      const response = await api.put(`/projects/${id}`, project);
      return response.data;
    } catch (error: any) {
      console.error(`[projectService] Error updating project ${id}:`, error);
      if (error.response?.status === 401) {
        throw new Error('You\'re not logged in or your session expired. Please refresh the page.');
      }
      throw new Error(error.response?.data?.detail || error.message || `Failed to update project ${id}`);
    }
  }

  async deleteProject(id: string): Promise<boolean> {
    try {
      // Use authenticated axios client - interceptor handles auth header
      await api.delete(`/projects/${id}`);
      return true;
    } catch (error: any) {
      console.error(`[projectService] Error deleting project ${id}:`, error);
      if (error.response?.status === 401) {
        throw new Error('You\'re not logged in or your session expired. Please refresh the page.');
      }
      throw new Error(error.response?.data?.detail || error.message || `Failed to delete project ${id}`);
    }
  }

  // Mock data for development (remove when backend is connected)
  getMockProjects(): Project[] {
    return [
      {
        id: "1",
        name: "Medical Device FMEA",
        description: "Failure Mode and Effects Analysis for new medical device",
        user_id: "user123",
        version_number: "1.0",
        major_version: 1,
        minor_version: 0,
        patch_version: 0,
        version_status: "draft",
        version_label: "Draft",
        change_summary: "Initial project setup",
        change_details: {},
        content_hash: "hash123",
        approval_required: "false",
        approved_by: null,
        approved_at: null,
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-15T10:00:00Z",
        version_created_at: "2024-01-15T10:00:00Z",
        version_updated_at: "2024-01-15T10:00:00Z"
      },
      {
        id: "2",
        name: "Process Improvement CAPA",
        description: "Corrective and Preventive Actions for manufacturing process",
        user_id: "user123",
        version_number: "2.1",
        major_version: 2,
        minor_version: 1,
        patch_version: 0,
        version_status: "approved",
        version_label: "Final",
        change_summary: "Process improvements implemented",
        change_details: {},
        content_hash: "hash456",
        approval_required: "true",
        approved_by: "admin",
        approved_at: "2024-01-12T09:15:00Z",
        created_at: "2024-01-10T14:30:00Z",
        updated_at: "2024-01-12T09:15:00Z",
        version_created_at: "2024-01-10T14:30:00Z",
        version_updated_at: "2024-01-12T09:15:00Z"
      },
      {
        id: "3",
        name: "Design Change Control",
        description: "Managing design changes for product improvement",
        user_id: "user123",
        version_number: "1.0",
        major_version: 1,
        minor_version: 0,
        patch_version: 0,
        version_status: "draft",
        version_label: "Draft",
        change_summary: "Initial design setup",
        change_details: {},
        content_hash: "hash789",
        approval_required: "false",
        approved_by: null,
        approved_at: null,
        created_at: "2024-01-08T09:00:00Z",
        updated_at: null,
        version_created_at: "2024-01-08T09:00:00Z",
        version_updated_at: "2024-01-08T09:00:00Z"
      }
    ];
  }
}

export default new ProjectService();
