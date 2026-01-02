// src/services/apiService.ts
import api from '../axios';

// Types
export interface Project {
  id: number;
  name: string;
  description?: string;
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
  updated_at: string;
  version_created_at: string;
  version_updated_at: string;
}

export interface FMEA {
  id: number;
  project_id: number;
  user_id: string;
  component: string;
  failure_mode: string;
  potential_effects: string;
  severity: number;
  potential_causes: string;
  occurrence: number;
  current_controls: string;
  detection: number;
  rpn: number;
  recommended_actions: string;
  responsibility: string;
  target_completion_date: string;
  actions_taken: string;
  final_severity: number;
  final_occurrence: number;
  final_detection: number;
  final_rpn: number;
  created_at: string;
  updated_at: string;
}

export interface CapaData {
  id: string;
  issue_description: string;
  source: string;
  detection_date: string;
  severity: string;
  root_cause: string;
  corrective_action: string;
  preventive_action: string;
  action_owner: string;
  due_date: string;
  status: string;
  effectiveness_check_plan: string;
  fmea_link: string;
  regulatory_impact: string;
  closure_summary: string;
  milestones: string;
  risk_controls_update: string;
  analysis_timestamp: string;
  version: string;
}

export interface CapaResponse {
  capa_data: CapaData[];
  mock: boolean;
}

export interface ChangeControlData {
  id: string;
  change_description: string;
  initiator: string;
  date_initiated: string;
  status: string;
  impact_assessment: string;
  actions_required: string;
  action_owner: string;
  due_date: string;
  closure_summary: string;
  analysis_timestamp: string;
  version: string;
}

export interface ChangeControlResponse {
  change_control_data: ChangeControlData[];
  mock: boolean;
}

// Fetch all projects
export const getProjects = async (): Promise<Project[]> => {
  try {
    console.log('ApiService: Calling api.get("/projects")...');
    const response = await api.get('/projects');
    console.log('ApiService: Projects response:', response.data);
    return response.data;
  } catch (error) {
    console.error('ApiService: Error fetching projects:', error);
    throw error;
  }
};

// Create a new project
export const createProject = async (projectData: { name: string; description?: string }): Promise<Project> => {
  try {
    const response = await api.post('/projects', projectData);
    return response.data;
  } catch (error) {
    console.error('Error creating project:', error);
    throw error;
  }
};

// Fetch all FMEAs
export const getFmeas = async (): Promise<FMEA[]> => {
  try {
    const response = await api.get('/fmeas');
    return response.data;
  } catch (error) {
    console.error('Error fetching FMEAs:', error);
    throw error;
  }
};

// Create a new FMEA
export const createFmea = async (fmeaData: any): Promise<FMEA> => {
  try {
    const response = await api.post('/fmeas', fmeaData);
    return response.data;
  } catch (error) {
    console.error('Error creating FMEA:', error);
    throw error;
  }
};

// Generate CAPA
export const generateCapa = async (issueDescription: string, capaType: string = 'corrective'): Promise<CapaResponse> => {
  try {
    const response = await api.post('/fmea/capa/generate', {
      issue_description: issueDescription,
      capa_type: capaType
    });
    return response.data;
  } catch (error) {
    console.error('Error generating CAPA:', error);
    throw error;
  }
};

// Generate Design Inputs
export interface DesignInputItem {
  title: string;
  requirement: string;
  description?: string;
}

export interface DesignInputsGenerateResponse {
  design_inputs: DesignInputItem[];
}

export const generateDesignInputs = async (componentName: string, count: number = 5): Promise<DesignInputsGenerateResponse> => {
  try {
    const response = await api.post('/ai/design-inputs/generate', {
      component_name: componentName,
      count: count
    });
    return response.data;
  } catch (error) {
    console.error('Error generating design inputs:', error);
    throw error;
  }
};

// Generate Design Outputs
export interface DesignOutputItem {
  title: string;
  specification: string;
  description?: string;
}

export interface DesignOutputsGenerateResponse {
  design_outputs: DesignOutputItem[];
}

export const generateDesignOutputs = async (componentName: string, count: number = 5): Promise<DesignOutputsGenerateResponse> => {
  try {
    const response = await api.post('/ai/design-outputs/generate', {
      component_name: componentName,
      count: count
    });
    return response.data;
  } catch (error) {
    console.error('Error generating design outputs:', error);
    throw error;
  }
};

// Health check for CAPA
export const capaHealth = async (): Promise<{ status: string; message: string }> => {
  try {
    const response = await api.get('/fmea/capa/health');
    return response.data;
  } catch (error) {
    console.error('Error checking CAPA health:', error);
    throw error;
  }
};

// Generate Change Control
export const generateChangeControl = async (changeDescription: string): Promise<ChangeControlResponse> => {
  try {
    console.log('Making API call to /fmea/change-control/generate with:', { change_description: changeDescription });
    const response = await api.post('/fmea/change-control/generate', {
      change_description: changeDescription
    });
    console.log('API response received:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Error generating Change Control:', error);
    console.error('Error details:', error.response?.data || error.message);
    throw error;
  }
}; 