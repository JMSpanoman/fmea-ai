// src/services/apiService.js
import api from '../axios';

// Fetch all projects
export const getProjects = async () => {
  try {
    const response = await api.get('/projects');
    return response.data;
  } catch (error) {
    console.error('Error fetching projects:', error);
    throw error;
  }
};

// Create a new project
export const createProject = async (projectData) => {
  try {
    const response = await api.post('/projects', projectData);
    return response.data;
  } catch (error) {
    console.error('Error creating project:', error);
    throw error;
  }
};

// Fetch all FMEAs
export const getFmeas = async () => {
  try {
    const response = await api.get('/fmeas');
    return response.data;
  } catch (error) {
    console.error('Error fetching FMEAs:', error);
    throw error;
  }
};

// Create a new FMEA
export const createFmea = async (fmeaData) => {
  try {
    const response = await api.post('/fmeas', fmeaData);
    return response.data;
  } catch (error) {
    console.error('Error creating FMEA:', error);
    throw error;
  }
};

// Generate CAPA
export const generateCapa = async (issueDescription, capaType = 'corrective') => {
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

// Health check for CAPA
export const capaHealth = async () => {
  try {
    const response = await api.get('/fmea/capa/health');
    return response.data;
  } catch (error) {
    console.error('Error checking CAPA health:', error);
    throw error;
  }
};
