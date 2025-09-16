// Using fetch instead of axios to match existing codebase

export interface Project {
  id: number;
  name: string;
  description: string | null;
  status: string;
  user_id: string;
  
  // Version control fields
  version_number: string;
  major_version: number;
  minor_version: number;
  patch_version: number;
  version_status: string;
  version_label: string | null;
  change_summary: string | null;
  change_details: any | null;
  content_hash: string | null;
  approval_required: string;
  approved_by: string | null;
  approved_at: string | null;
  
  // Timestamps
  created_at: string;
  updated_at: string | null;
  version_created_at: string;
  version_updated_at: string;
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
  private baseUrl = 'http://localhost:8000/projects';
  private authUrl = 'http://localhost:8000/auth/dev-login';
  private token: string | null = null;

  private async getAuthToken(): Promise<string> {
    if (this.token) {
      return this.token;
    }

    try {
      const response = await fetch(this.authUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Auth failed: ${response.status}`);
      }

      const authData = await response.json();
      this.token = authData.access_token;
      return authData.access_token;
    } catch (error) {
      console.error('Error getting auth token:', error);
      throw error;
    }
  }

  async getProjects(): Promise<Project[]> {
    try {
      const token = await this.getAuthToken();
      
      const response = await fetch(`${this.baseUrl}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching projects:', error);
      throw error;
    }
  }

  async getProject(id: number): Promise<Project> {
    try {
      const token = await this.getAuthToken();
      
      const response = await fetch(`${this.baseUrl}/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error fetching project ${id}:`, error);
      throw error;
    }
  }

  async createProject(project: ProjectCreate): Promise<Project> {
    try {
      const token = await this.getAuthToken();
      
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(project),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error creating project:', error);
      throw error;
    }
  }

  async updateProject(id: number, project: ProjectUpdate): Promise<Project> {
    try {
      const token = await this.getAuthToken();
      
      const response = await fetch(`${this.baseUrl}/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(project),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error updating project ${id}:`, error);
      throw error;
    }
  }

  async deleteProject(id: number): Promise<boolean> {
    try {
      const token = await this.getAuthToken();
      
      const response = await fetch(`${this.baseUrl}/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return true;
    } catch (error) {
      console.error(`Error deleting project ${id}:`, error);
      throw error;
    }
  }

  // Mock data for development (remove when backend is connected)
  getMockProjects(): Project[] {
    return [
      {
        id: 1,
        name: "Medical Device FMEA",
        description: "Failure Mode and Effects Analysis for new medical device",
        status: "draft",
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
        id: 2,
        name: "Process Improvement CAPA",
        description: "Corrective and Preventive Actions for manufacturing process",
        status: "final",
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
        id: 3,
        name: "Design Change Control",
        description: "Managing design changes for product improvement",
        status: "draft",
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
