import React, { useState, useEffect } from 'react';
import { Project } from '../services/apiService';
import { useProject } from '../contexts/ProjectContext';
import projectService from '../services/projectService';

interface ProjectSelectorProps {
  className?: string;
  showLabel?: boolean;
  compact?: boolean;
}

const ProjectSelector: React.FC<ProjectSelectorProps> = ({ 
  className = '', 
  showLabel = true,
  compact = false 
}) => {
  const { currentProject, setCurrentProject, isProjectSelected } = useProject();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await projectService.getProjects();
      setProjects(data);
      setError(null);
    } catch (err) {
      setError('Failed to load projects');
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleProjectSelect = (project: Project) => {
    // Only change project if a different one is selected
    if (!currentProject || currentProject.id !== project.id) {
      setCurrentProject(project);
    }
    setIsOpen(false);
  };

  const handleClearProject = () => {
    setCurrentProject(null);
    setIsOpen(false);
  };

  const getProjectStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      case 'final': return 'bg-green-100 text-green-800';
      case 'exported': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (compact) {
    return (
      <div className={`relative ${className}`}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <i className="fa-solid fa-folder-tree text-gray-400"></i>
          <span className="truncate max-w-32">
            {currentProject ? currentProject.name : 'Select Project'}
          </span>
          <i className={`fa-solid fa-chevron-down text-xs text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}></i>
        </button>

        {isOpen && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-50 max-h-60 overflow-y-auto">
            {loading ? (
              <div className="px-3 py-2 text-sm text-gray-500">Loading projects...</div>
            ) : error ? (
              <div className="px-3 py-2 text-sm text-red-500">{error}</div>
            ) : (
              <>
                {projects.map((project) => (
                  <button
                    key={project.id}
                    onClick={() => handleProjectSelect(project)}
                    className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 ${
                      currentProject?.id === project.id ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="truncate">{project.name}</span>
                      {currentProject?.id === project.id && (
                        <i className="fa-solid fa-check text-blue-600"></i>
                      )}
                    </div>
                  </button>
                ))}
                {currentProject && (
                  <button
                    onClick={handleClearProject}
                    className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 border-t border-gray-200"
                  >
                    <i className="fa-solid fa-times mr-2"></i>
                    Clear Selection
                  </button>
                )}
              </>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {showLabel && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Current Project
        </label>
      )}
      
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between px-4 py-3 text-left bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <i className="fa-solid fa-folder-tree text-blue-600"></i>
            </div>
            <div className="flex-1 min-w-0">
              {currentProject ? (
                <>
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {currentProject.name}
                  </div>
                  <div className="text-sm text-gray-500 truncate">
                    {currentProject.description || 'No description'}
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getProjectStatusColor(currentProject.status)}`}>
                      {currentProject.status || 'Unknown'}
                    </span>
                    <span className="text-xs text-gray-400">
                      Last updated: {new Date(currentProject.updated_at || currentProject.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </>
              ) : (
                <div className="text-sm text-gray-500">No project selected</div>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {currentProject && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Active
              </span>
            )}
            <i className={`fa-solid fa-chevron-down text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}></i>
          </div>
        </button>

        {isOpen && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto">
            <div className="p-3 border-b border-gray-200">
              <h3 className="text-sm font-medium text-gray-900">Select Project</h3>
              <p className="text-xs text-gray-500 mt-1">
                Choose a project to work with. Only changes when explicitly selected.
              </p>
            </div>
            
            {loading ? (
              <div className="px-3 py-4 text-center text-sm text-gray-500">
                <i className="fa-solid fa-spinner fa-spin mr-2"></i>
                Loading projects...
              </div>
            ) : error ? (
              <div className="px-3 py-4 text-center text-sm text-red-500">
                <i className="fa-solid fa-exclamation-triangle mr-2"></i>
                {error}
              </div>
            ) : (
              <div className="p-2">
                {projects.map((project) => (
                  <button
                    key={project.id}
                    onClick={() => handleProjectSelect(project)}
                    className={`w-full text-left p-3 rounded-md hover:bg-gray-50 transition-colors ${
                      currentProject?.id === project.id ? 'bg-blue-50 border border-blue-200' : ''
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                        <i className="fa-solid fa-folder text-gray-600 text-sm"></i>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className={`text-sm font-medium truncate ${
                            currentProject?.id === project.id ? 'text-blue-700' : 'text-gray-900'
                          }`}>
                            {project.name}
                          </span>
                          {currentProject?.id === project.id && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              Current
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500 truncate mt-1">
                          {project.description || 'No description'}
                        </div>
                        <div className="flex items-center space-x-2 mt-2">
                          <span className={`inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium ${getProjectStatusColor(project.status)}`}>
                            {project.status || 'Unknown'}
                          </span>
                          <span className="text-xs text-gray-400">
                            {new Date(project.updated_at || project.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        {/* Version Control Information */}
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-xs text-gray-500">
                            v{project.version_number || '1.0'}
                          </span>
                          {project.version_status && (
                            <span className={`inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium ${
                              project.version_status === 'approved' ? 'bg-green-100 text-green-800' :
                              project.version_status === 'review' ? 'bg-yellow-100 text-yellow-800' :
                              project.version_status === 'draft' ? 'bg-gray-100 text-gray-800' :
                              'bg-blue-100 text-blue-800'
                            }`}>
                              {project.version_status}
                            </span>
                          )}
                          {project.approval_required === 'true' && (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                              Approval Required
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
                
                {currentProject && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <button
                      onClick={handleClearProject}
                      className="w-full text-left p-3 rounded-md text-red-600 hover:bg-red-50 transition-colors"
                    >
                      <i className="fa-solid fa-times mr-2"></i>
                      Clear Project Selection
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Current Project Info */}
      {currentProject && (
        <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <i className="fa-solid fa-info-circle text-blue-600"></i>
              <span className="text-sm font-medium text-blue-900">Working on:</span>
              <span className="text-sm text-blue-800">{currentProject.name}</span>
            </div>
            <span className="text-xs text-blue-600">
              Project ID: {currentProject.id}
            </span>
          </div>
          <p className="text-xs text-blue-700 mt-1">
            All documents and reports will be associated with this project until you select a different one.
          </p>
          {/* Version Control Details */}
          <div className="mt-2 pt-2 border-t border-blue-200">
            <div className="flex items-center space-x-4 text-xs">
              <div className="flex items-center space-x-1">
                <span className="text-blue-600">Version:</span>
                <span className="font-medium">{currentProject.version_number || '1.0'}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-blue-600">Status:</span>
                <span className={`px-1.5 py-0.5 rounded-full font-medium ${
                  currentProject.version_status === 'approved' ? 'bg-green-100 text-green-800' :
                  currentProject.version_status === 'review' ? 'bg-yellow-100 text-yellow-800' :
                  currentProject.version_status === 'draft' ? 'bg-gray-100 text-gray-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {currentProject.version_status || 'draft'}
                </span>
              </div>
              {currentProject.approval_required === 'true' && (
                <div className="flex items-center space-x-1">
                  <span className="text-orange-600">Approval:</span>
                  <span className="px-1.5 py-0.5 rounded-full font-medium bg-orange-100 text-orange-800">
                    Required
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectSelector;
