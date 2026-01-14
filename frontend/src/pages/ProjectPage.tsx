import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import projectService, { Project, ProjectCreate } from '../services/projectService';
import authService from '../services/authService';
import { useProject } from '../contexts/ProjectContext';

interface ProjectFormData {
  name: string;
  description: string;
}

const ProjectPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [formData, setFormData] = useState<ProjectFormData>({
    name: '',
    description: ''
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const navigate = useNavigate();
  const { setCurrentProject } = useProject();

  // Load projects from service
  useEffect(() => {
    const loadProjects = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Ensure authentication before loading projects
        if (!authService.isAuthenticated()) {
          console.log('[ProjectPage] Not authenticated, attempting to authenticate...');
          try {
            await authService.authenticate();
            console.log('[ProjectPage] Authentication successful');
          } catch (authError) {
            console.error('[ProjectPage] Authentication failed:', authError);
            setError('Failed to authenticate. Please refresh the page.');
            setLoading(false);
            return;
          }
        } else {
          console.log('[ProjectPage] Already authenticated');
        }
        
        // Small delay to ensure token is in localStorage
        await new Promise(resolve => setTimeout(resolve, 100));
        
        console.log('[ProjectPage] Loading projects...');
        const token = localStorage.getItem('token');
        console.log('[ProjectPage] Token available:', !!token);
        
        const projects = await projectService.getProjects();
        console.log('[ProjectPage] Projects loaded:', projects?.length || 0, 'projects');
        setProjects(projects || []);
      } catch (error: any) {
        console.error('[ProjectPage] Error loading projects:', error);
        const errorMessage = error.message || error.response?.data?.detail || 'Unknown error';
        if (errorMessage.includes('not logged in') || errorMessage.includes('session expired') || error.response?.status === 401) {
          setError('You\'re not logged in or your session expired. Please refresh the page.');
        } else {
          setError(`Failed to load projects: ${errorMessage}. Please try refreshing the page.`);
        }
      } finally {
        setLoading(false);
      }
    };

    loadProjects();
  }, []);

  const handleCreateProject = async () => {
    if (!formData.name.trim()) {
      setError('Project name is required');
      return;
    }

    try {
      const projectData: ProjectCreate = {
        name: formData.name,
        description: formData.description
      };

      const newProject = await projectService.createProject(projectData);
      setProjects([...projects, newProject]);
      setFormData({ name: '', description: '' });
      setShowCreateForm(false);
      setSuccess('Project created successfully!');
      setTimeout(() => setSuccess(null), 3000);

      // Project-first workflow: select + persist + navigate into Setup Wizard
      setCurrentProject(newProject as any);
      navigate(`/projects/${newProject.id}/setup`);
    } catch (error: any) {
      console.error('[ProjectPage] Error creating project:', error);
      if (error.message?.includes('not logged in') || error.message?.includes('session expired') || error.response?.status === 401) {
        setError('You\'re not logged in or your session expired. Please refresh the page.');
      } else {
        setError(error.message || 'Failed to create project');
      }
    }
  };

  const handleEditProject = (project: Project) => {
    setEditingProject(project);
    setFormData({
      name: project.name,
      description: project.description || ''
    });
    setShowCreateForm(true);
  };

  const handleUpdateProject = async () => {
    if (!editingProject || !formData.name.trim()) {
      setError('Project name is required');
      return;
    }

    try {
      const updatedProject = await projectService.updateProject(editingProject.id, {
        name: formData.name,
        description: formData.description
      });

      setProjects(projects.map(p => 
        p.id === editingProject.id ? updatedProject : p
      ));

      setFormData({ name: '', description: '' });
      setEditingProject(null);
      setShowCreateForm(false);
      setSuccess('Project updated successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (error) {
      console.error('Error updating project:', error);
      setError('Failed to update project');
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await projectService.deleteProject(projectId);
        setProjects(projects.filter(p => p.id !== projectId));
        setSuccess('Project deleted successfully!');
        setTimeout(() => setSuccess(null), 3000);
      } catch (error) {
        console.error('Error deleting project:', error);
        setError('Failed to delete project');
      }
    }
  };

  const handleOpenProject = (project: Project) => {
    // Navigate to project-specific page or open project
    setCurrentProject(project as any);
    navigate(`/projects/${project.id}/docs`);
  };

  const getStatusBadge = (status?: string) => {
    const statusConfig = {
      draft: { color: 'bg-yellow-100 text-yellow-800', label: 'Draft' },
      final: { color: 'bg-green-100 text-green-800', label: 'Final' },
      exported: { color: 'bg-blue-100 text-blue-800', label: 'Exported' }
    };
    
    const key = (status || 'draft') as keyof typeof statusConfig;
    const config = statusConfig[key] || statusConfig.draft;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Project Center</h1>
            <p className="text-gray-600 mt-2">Manage your FMEA projects and quality management documents</p>
          </div>
          <button
            onClick={() => {
              setShowCreateForm(true);
              setEditingProject(null);
              setFormData({ name: '', description: '' });
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            New Project
          </button>
        </div>

        {/* Alerts */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
            <button onClick={() => setError(null)} className="float-right font-bold">&times;</button>
          </div>
        )}
        
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
            {success}
            <button onClick={() => setSuccess(null)} className="float-right font-bold">&times;</button>
          </div>
        )}

        {/* Create/Edit Form */}
        {showCreateForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">
              {editingProject ? 'Edit Project' : 'Create New Project'}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter project name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Enter project description"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-4">
              <button
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingProject(null);
                  setFormData({ name: '', description: '' });
                }}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={editingProject ? handleUpdateProject : handleCreateProject}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                {editingProject ? 'Update Project' : 'Create Project'}
              </button>
            </div>
          </div>
        )}

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div key={project.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">{project.name}</h3>
                  {getStatusBadge(project.status)}
                </div>
                
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {project.description || 'No description provided'}
                </p>
                
                <div className="text-xs text-gray-500 mb-4">
                  <div>Created: {new Date(project.created_at).toLocaleDateString()}</div>
                  {project.updated_at && (
                    <div>Updated: {new Date(project.updated_at).toLocaleDateString()}</div>
                  )}
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleOpenProject(project)}
                    className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md text-sm hover:bg-blue-700 transition-colors"
                  >
                    Open
                  </button>
                  <button
                    onClick={() => handleEditProject(project)}
                    className="px-3 py-2 text-gray-600 border border-gray-300 rounded-md text-sm hover:bg-gray-50 transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteProject(project.id)}
                    className="px-3 py-2 text-red-600 border border-red-300 rounded-md text-sm hover:bg-red-50 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {projects.length === 0 && !showCreateForm && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No projects</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by creating a new project.</p>
            <div className="mt-6">
              <button
                onClick={() => setShowCreateForm(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <svg className="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                New Project
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectPage; 