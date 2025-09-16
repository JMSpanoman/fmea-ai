import React, { useState, useEffect } from 'react';

// Import FMEAApi from the global window object since it's exported as a global
declare global {
  interface Window {
    FMEAApi: any;
  }
}

interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

interface ProjectsSidebarProps {
  onProjectSelect: (project: Project) => void;
  selectedProjectId?: number;
}

const ProjectsSidebar: React.FC<ProjectsSidebarProps> = ({ onProjectSelect, selectedProjectId }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });

  const api = new window.FMEAApi();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await api.getProjects();
      setProjects(data);
      setError(null);
    } catch (err) {
      setError('Failed to load projects');
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProject.name.trim()) return;

    try {
      const createdProject = await api.createProject(newProject);
      setProjects([...projects, createdProject]);
      setNewProject({ name: '', description: '' });
      setShowCreateForm(false);
      setError(null);
    } catch (err) {
      setError('Failed to create project');
      console.error('Error creating project:', err);
    }
  };

  const handleDeleteProject = async (projectId: number) => {
    if (!confirm('Are you sure you want to delete this project?')) return;

    try {
      await api.deleteProject(projectId);
      setProjects(projects.filter(p => p.id !== projectId));
      setError(null);
    } catch (err) {
      setError('Failed to delete project');
      console.error('Error deleting project:', err);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="w-80 h-full bg-gray-50 border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">Projects</h2>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            title="Create new project"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>
      </div>

      {/* Create Project Form */}
      {showCreateForm && (
        <div className="p-4 border-b border-gray-200 bg-white">
          <form onSubmit={handleCreateProject} className="space-y-3">
            <div>
              <input
                type="text"
                placeholder="Project name"
                value={newProject.name}
                onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <textarea
                placeholder="Description (optional)"
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={2}
              />
            </div>
            <div className="flex space-x-2">
              <button
                type="submit"
                className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-3 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border-b border-red-200">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* Projects List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-center text-gray-500">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2">Loading projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <svg className="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>No projects yet</p>
            <p className="text-sm">Create your first project to get started</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {projects.map((project) => (
              <div
                key={project.id}
                className={`p-4 hover:bg-gray-100 cursor-pointer transition-colors ${
                  selectedProjectId === project.id ? 'bg-blue-50 border-r-2 border-blue-600' : ''
                }`}
                onClick={() => onProjectSelect(project)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {project.name}
                    </h3>
                    {project.description && (
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                        {project.description}
                      </p>
                    )}
                    <div className="flex items-center mt-2 text-xs text-gray-400">
                      <span>Created: {formatDate(project.created_at)}</span>
                      {project.updated_at !== project.created_at && (
                        <span className="ml-2">Updated: {formatDate(project.updated_at)}</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteProject(project.id);
                    }}
                    className="ml-2 p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="Delete project"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectsSidebar; 