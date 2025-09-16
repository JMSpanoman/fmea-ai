import React, { useState, useEffect } from 'react';
import { getProjects, Project } from '../services/apiService';
import authService from '../services/authService';

const TestProjects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [authStatus, setAuthStatus] = useState<string>('Not tested');

  useEffect(() => {
    testProjects();
  }, []);

  const testProjects = async () => {
    try {
      setLoading(true);
      setAuthStatus('Testing authentication...');
      
      // Test authentication
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
        setAuthStatus('Authentication successful');
      } else {
        setAuthStatus('Already authenticated');
      }
      
      // Test projects fetch
      const data = await getProjects();
      setProjects(data);
      setError(null);
    } catch (err) {
      console.error('Error testing projects:', err);
      setError(`Failed to load projects: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Projects Test Page</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
          <p className="mb-4">Status: <span className="font-mono">{authStatus}</span></p>
          <button 
            onClick={testProjects}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Test Projects
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Projects ({projects.length})</h2>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p>Loading projects...</p>
            </div>
          ) : error ? (
            <div className="text-red-600 p-4 bg-red-50 rounded">
              {error}
            </div>
          ) : projects.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No projects found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {projects.map((project) => (
                <div key={project.id} className="border p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-lg">{project.name}</h3>
                      <p className="text-gray-600">{project.description || 'No description'}</p>
                      <p className="text-sm text-gray-500">ID: {project.id} | Status: {project.status}</p>
                      <p className="text-sm text-gray-500">Created: {new Date(project.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="text-right">
                      <span className="inline-block w-3 h-3 bg-green-500 rounded-full"></span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TestProjects; 