import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import ProjectSelector from '../components/ProjectSelector';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { currentProject, isProjectSelected } = useProject();

  const handleStartNewFmea = () => {
    if (!isProjectSelected) {
      alert('Please select a project first before starting FMEA analysis.');
      return;
    }
    navigate('/dfmea');
  };

  const handleStartNewDesignControl = () => {
    if (!isProjectSelected) {
      alert('Please select a project first before starting design control.');
      return;
    }
    navigate('/traceability-matrix');
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Welcome to Foton aiQMS</h1>
        <p className="text-lg text-gray-600 mt-2">Your comprehensive quality management platform</p>
      </div>

      {/* Current Project Section */}
      <div className="mb-8">
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Current Project</h2>
            <ProjectSelector compact={true} showLabel={false} />
          </div>
          
          {currentProject ? (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <i className="fa-solid fa-folder-tree text-blue-600 text-xl"></i>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-blue-900">{currentProject.name}</h3>
                  <p className="text-sm text-blue-700">{currentProject.description || 'No description available'}</p>
                  <div className="flex items-center space-x-4 mt-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      currentProject.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                      currentProject.status === 'final' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {currentProject.status || 'Unknown Status'}
                    </span>
                    <span className="text-xs text-blue-600">
                      Project ID: {currentProject.id}
                    </span>
                    <span className="text-xs text-blue-600">
                      Last updated: {new Date(currentProject.updated_at || currentProject.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              <div className="mt-4 p-3 bg-blue-100 rounded-md">
                <p className="text-sm text-blue-800">
                  <i className="fa-solid fa-info-circle mr-2"></i>
                  All documents, reports, and analyses will be associated with this project until you select a different one.
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <i className="fa-solid fa-exclamation-triangle text-yellow-600 text-xl"></i>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-yellow-900">No Project Selected</h3>
                  <p className="text-sm text-yellow-700">
                    Please select a project to start working with FMEA analysis, CAPA management, and other quality processes.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-8 mb-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {isProjectSelected ? `Ready to work on ${currentProject?.name}` : 'Get Started Today'}
          </h2>
          <p className="text-lg text-gray-600 mb-6">
            {isProjectSelected 
              ? 'Choose your next action to continue managing quality processes for this project'
              : 'Choose your next action to begin managing quality processes'
            }
          </p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={handleStartNewFmea}
              disabled={!isProjectSelected}
              className={`px-6 py-3 rounded-lg transition-colors ${
                isProjectSelected
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-400 text-gray-200 cursor-not-allowed'
              }`}
            >
              Start New FMEA
            </button>
            <button
              onClick={handleStartNewDesignControl}
              disabled={!isProjectSelected}
              className={`px-6 py-3 rounded-lg transition-colors ${
                isProjectSelected
                  ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                  : 'bg-gray-400 text-gray-200 cursor-not-allowed'
              }`}
            >
              Design Control
            </button>
            <button
              onClick={() => navigate('/projects')}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
            >
              Manage Projects
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="space-y-8">
        {/* Quick Actions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* FMEA Builder */}
          <div className={`bg-white rounded-lg shadow p-6 transition-shadow ${
            isProjectSelected ? 'hover:shadow-lg' : 'opacity-75'
          }`}>
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <i className="fa-solid fa-shield-halved text-blue-600 text-xl"></i>
              </div>
              <h3 className="text-lg font-semibold text-gray-900">FMEA Builder</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Create and manage Failure Mode and Effects Analysis documents with AI assistance.
            </p>
            <button
              onClick={() => navigate('/dfmea')}
              disabled={!isProjectSelected}
              className={`font-medium ${
                isProjectSelected
                  ? 'text-blue-600 hover:text-blue-700'
                  : 'text-gray-400 cursor-not-allowed'
              }`}
            >
              {isProjectSelected ? 'Get Started →' : 'Select Project First'}
            </button>
          </div>

          {/* CAPA Management */}
          <div className={`bg-white rounded-lg shadow p-6 transition-shadow ${
            isProjectSelected ? 'hover:shadow-lg' : 'opacity-75'
          }`}>
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                <i className="fa-solid fa-clipboard-check text-green-600 text-xl"></i>
              </div>
              <h3 className="text-lg font-semibold text-gray-900">CAPA Management</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Track and manage Corrective and Preventive Actions with automated workflows.
            </p>
            <button
              onClick={() => navigate('/capa')}
              disabled={!isProjectSelected}
              className={`font-medium ${
                isProjectSelected
                  ? 'text-green-600 hover:text-green-700'
                  : 'text-gray-400 cursor-not-allowed'
              }`}
            >
              {isProjectSelected ? 'View CAPAs →' : 'Select Project First'}
            </button>
          </div>

          {/* Change Control */}
          <div className={`bg-white rounded-lg shadow p-6 transition-shadow ${
            isProjectSelected ? 'hover:shadow-lg' : 'opacity-75'
          }`}>
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                <i className="fa-solid fa-arrows-rotate text-purple-600 text-xl"></i>
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Change Control</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Manage design changes and control processes with comprehensive tracking.
            </p>
            <button
              onClick={() => navigate('/change-control')}
              disabled={!isProjectSelected}
              className={`font-medium ${
                isProjectSelected
                  ? 'text-purple-600 hover:text-purple-700'
                  : 'text-gray-400 cursor-not-allowed'
              }`}
            >
              {isProjectSelected ? 'Manage Changes →' : 'Select Project First'}
            </button>
          </div>
        </div>

        {/* Project Status Summary */}
        {isProjectSelected && currentProject && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Status Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">0</div>
                <div className="text-sm text-gray-600">FMEA Documents</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">0</div>
                <div className="text-sm text-gray-600">CAPA Records</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">0</div>
                <div className="text-sm text-gray-600">Change Controls</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
 