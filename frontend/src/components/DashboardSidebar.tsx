import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { getProjects, Project } from '../services/apiService';
import authService from '../services/authService';
import ProjectDataViewer from './ProjectDataViewer';
import ErrorBoundary from './ErrorBoundary';
import UserProfileModal from './UserProfileModal';
import CreateProjectModal from './CreateProjectModal';
import DeleteProjectModal from './DeleteProjectModal';

interface DashboardSidebarProps {
  onProjectSelect?: (project: Project) => void;
  selectedProjectId?: number;
  selectedProject?: Project;
}

const DashboardSidebar: React.FC<DashboardSidebarProps> = ({ 
  onProjectSelect, 
  selectedProjectId,
  selectedProject
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedProjects, setExpandedProjects] = useState(false);
  const [expandedRiskManagement, setExpandedRiskManagement] = useState(true);
  const [expandedDesignControl, setExpandedDesignControl] = useState(false);
  const [expandedQualityManagement, setExpandedQualityManagement] = useState(false);
  const [showProjectDataViewer, setShowProjectDataViewer] = useState(false);
  const [selectedProjectForViewer, setSelectedProjectForViewer] = useState<Project | null>(null);
  const [showUserProfileModal, setShowUserProfileModal] = useState(false);
  const [showCreateProjectModal, setShowCreateProjectModal] = useState(false);
  const [showDeleteProjectModal, setShowDeleteProjectModal] = useState(false);
  const [selectedProjectForDeletion, setSelectedProjectForDeletion] = useState<Project | null>(null);

  useEffect(() => {
    initializeAuthAndFetchProjects();
  }, []);

  const initializeAuthAndFetchProjects = async () => {
    try {
      setLoading(true);
      
      // First authenticate
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      
      // Then fetch projects
      await fetchProjects();
    } catch (err) {
      console.error('Failed to initialize:', err);
      setError('Failed to authenticate or load projects');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data);
      setError(null);
    } catch (err) {
      setError('Failed to load projects');
      console.error('Error fetching projects:', err);
    }
  };

  const handleProjectSelect = (project: Project) => {
    // Open the project data viewer
    setSelectedProjectForViewer(project);
    setShowProjectDataViewer(true);
    
    // Also call the original onProjectSelect if provided
    if (onProjectSelect) {
      onProjectSelect(project);
    }
  };

  const toggleProjectsExpansion = () => {
    setExpandedProjects(!expandedProjects);
  };

  const isActiveRoute = (path: string) => {
    return location.pathname === path;
  };

  const getActiveClass = (path: string) => {
    return isActiveRoute(path) 
      ? 'bg-blue-600 text-white' 
      : 'text-gray-700 hover:bg-gray-100';
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const handleOpenUserProfile = () => {
    const userData = localStorage.getItem('user');
    if (userData && userData !== 'undefined' && userData !== 'null') {
      try {
        JSON.parse(userData); // Test if it's valid JSON
        setShowUserProfileModal(true);
      } catch (error) {
        console.error('Invalid user data, redirecting to login');
        handleLogout();
      }
    } else {
      console.error('No user data found, redirecting to login');
      handleLogout();
    }
  };

  const handleCloseUserProfile = () => {
    setShowUserProfileModal(false);
  };

  const handleOpenCreateProject = () => {
    setShowCreateProjectModal(true);
  };

  const handleCloseCreateProject = () => {
    setShowCreateProjectModal(false);
  };

  const handleProjectCreated = (newProject: any) => {
    // Refresh the projects list
    fetchProjects();
    // Close the modal
    setShowCreateProjectModal(false);
  };

  return (
    <aside className="w-64 bg-gray-800 text-white h-screen overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <button 
              onClick={() => {
                console.log('Logo clicked, navigating to /welcome');
                navigate('/welcome');
              }}
              className="flex items-center hover:opacity-80 transition-opacity cursor-pointer"
            >
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-sm">F</span>
              </div>
              <span className="font-bold text-lg">Foton aiQMS</span>
            </button>
          </div>
        </div>
        
        {/* User Profile Section */}
        <div className="flex items-center space-x-3 p-3 bg-gray-700 rounded-lg">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold text-sm">
              {(() => {
                const user = localStorage.getItem('user');
                if (user && user !== 'undefined' && user !== 'null') {
                  try {
                    const userData = JSON.parse(user);
                    return userData.username ? userData.username.charAt(0).toUpperCase() : 'U';
                  } catch (error) {
                    console.error('Error parsing user data:', error);
                    return 'U';
                  }
                }
                return 'U';
              })()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">
              {(() => {
                const user = localStorage.getItem('user');
                if (user && user !== 'undefined' && user !== 'null') {
                  try {
                    const userData = JSON.parse(user);
                    return userData.full_name || userData.username || 'User';
                  } catch (error) {
                    console.error('Error parsing user data:', error);
                    return 'User';
                  }
                }
                return 'User';
              })()}
            </p>
            <p className="text-xs text-gray-300 truncate">
              {(() => {
                const user = localStorage.getItem('user');
                if (user && user !== 'undefined' && user !== 'null') {
                  try {
                    const userData = JSON.parse(user);
                    return userData.role ? userData.role.charAt(0).toUpperCase() + userData.role.slice(1) : 'User';
                  } catch (error) {
                    console.error('Error parsing user data:', error);
                    return 'User';
                  }
                }
                return 'User';
              })()}
            </p>
          </div>
          <button
            onClick={handleOpenUserProfile}
            className="text-gray-300 hover:text-white transition-colors"
            title="View Profile"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Current Project Section */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-400">CURRENT PROJECT</h3>
          <button className="text-gray-400 hover:text-white">
            <i className="fa-solid fa-cog text-sm"></i>
          </button>
        </div>
        <div className="bg-gray-700 rounded-md p-2 flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span className="font-medium">
              {selectedProject ? selectedProject.name : 'No Project Selected'}
            </span>
          </div>
          <button 
            onClick={toggleProjectsExpansion}
            className="text-gray-400 hover:text-white transition-transform duration-200"
            style={{ transform: expandedProjects ? 'rotate(180deg)' : 'rotate(0deg)' }}
          >
            <i className="fa-solid fa-chevron-down text-xs"></i>
          </button>
        </div>
        {selectedProject && (
          <div className="text-xs text-gray-400 mt-1 text-center">
            Click any project to view its data
          </div>
        )}
        
        {/* Expandable Projects Section */}
        {expandedProjects && (
          <div className="mt-3 bg-gray-700 rounded-md p-3">
            {/* Create New Project Button */}
            <button
              onClick={handleOpenCreateProject}
              className="w-full bg-green-600 hover:bg-green-700 text-black text-sm py-2 px-3 rounded-md transition-colors flex items-center justify-center mb-3"
            >
              <i className="fa-solid fa-plus mr-2"></i>
              Create New Project
            </button>
            
            {loading ? (
              <div className="text-center text-gray-400 text-sm">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400 mx-auto mb-2"></div>
                Loading projects...
              </div>
            ) : error ? (
              <div className="text-red-400 text-sm">{error}</div>
            ) : projects.length === 0 ? (
              <div className="text-center">
                <div className="text-gray-400 text-sm mb-3">No projects available</div>
                <button
                  onClick={handleOpenCreateProject}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-black text-sm py-2 px-3 rounded-md transition-colors flex items-center justify-center"
                >
                  <i className="fa-solid fa-plus mr-2"></i>
                  Create New Project
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                {projects.map((project) => (
                  <div
                    key={project.id}
                    onClick={() => handleProjectSelect(project)}
                    className={`flex items-center justify-between p-2 rounded cursor-pointer transition-colors ${
                      selectedProjectId === project.id 
                        ? 'bg-blue-600 text-white' 
                        : 'hover:bg-gray-600 text-gray-300'
                    }`}
                    title="Click to view project data"
                  >
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                      <span className="text-sm truncate">{project.name}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <i className="fa-solid fa-eye text-xs opacity-60" title="View data"></i>
                      {selectedProjectId === project.id && (
                        <i className="fa-solid fa-check text-xs"></i>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <i className="fa-solid fa-search absolute left-3 top-2.5 text-gray-400"></i>
        <input 
          type="text" 
          placeholder="Search..." 
          className="w-full bg-gray-700 rounded-md pl-10 pr-4 py-2 text-sm border border-gray-600 focus:outline-none focus:border-blue-500" 
        />
      </div>

      {/* Navigation Sections */}
      <div className="p-4 space-y-6">
        {/* Main Navigation */}
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-3">MAIN NAVIGATION</h3>
          <ul className="space-y-1">
            <li>
              <button 
                onClick={() => navigate('/dashboard')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${getActiveClass('/dashboard')}`}
              >
                <i className="fa-solid fa-chart-line w-5 h-5 mr-3"></i>
                <span>Dashboard</span>
              </button>
            </li>
            <li>
              <button 
                onClick={() => navigate('/builder')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${getActiveClass('/builder')}`}
              >
                <i className="fa-solid fa-shield-halved w-5 h-5 mr-3"></i>
                <span>FMEA Builder</span>
              </button>
            </li>
            <li>
              <button 
                onClick={() => navigate('/capa')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${getActiveClass('/capa')}`}
              >
                <i className="fa-solid fa-check-double w-5 h-5 mr-3"></i>
                <span>CAPA</span>
              </button>
            </li>
            <li>
              <button 
                onClick={() => navigate('/change-control')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${getActiveClass('/change-control')}`}
              >
                <i className="fa-solid fa-arrows-rotate w-5 h-5 mr-3"></i>
                <span>Change Control</span>
              </button>
            </li>
            <li>
              <button 
                onClick={() => navigate('/non-conformance')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${getActiveClass('/non-conformance')}`}
              >
                <i className="fa-solid fa-triangle-exclamation w-5 h-5 mr-3"></i>
                <span>Non-Conformance</span>
              </button>
            </li>
          </ul>
        </div>

        {/* Risk Management Section */}
        <div>
          <button 
            onClick={() => setExpandedRiskManagement(!expandedRiskManagement)}
            className="flex items-center justify-between w-full text-left px-3 py-2 rounded-md text-gray-300 hover:bg-gray-700 transition-colors"
          >
            <div className="flex items-center">
              <i className="fa-solid fa-shield-halved w-5 h-5 mr-3"></i>
              <span>Risk Management</span>
            </div>
            <i className={`fa-solid fa-chevron-down text-xs transition-transform duration-200 ${
              expandedRiskManagement ? 'rotate-180' : ''
            }`}></i>
          </button>
          {expandedRiskManagement && (
            <div className="ml-8 mt-2 space-y-1">
              <button 
                onClick={() => navigate('/builder')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/builder') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-regular fa-file-lines w-4 h-4 mr-2"></i>
                <span>Design FMEA</span>
              </button>
              <button 
                onClick={() => navigate('/mitigation')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/mitigation') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-regular fa-file-lines w-4 h-4 mr-2"></i>
                <span>Process FMEA</span>
              </button>
              <button 
                onClick={() => navigate('/post-market')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/post-market') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-regular fa-file-lines w-4 h-4 mr-2"></i>
                <span>Post-Market</span>
              </button>
              <button 
                onClick={() => navigate('/hazard-analysis')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/hazard-analysis') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-exclamation-triangle w-4 h-4 mr-2"></i>
                <span>Hazard Analysis</span>
              </button>
              <button 
                onClick={() => navigate('/risk-evaluation-report')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/risk-evaluation-report') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-chart-line w-4 h-4 mr-2"></i>
                <span>Risk Evaluation Report</span>
              </button>
              <button 
                onClick={() => navigate('/risk-control-implementation')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/risk-control-implementation') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-shield-check w-4 h-4 mr-2"></i>
                <span>Risk Control Implementation</span>
              </button>
              <button 
                onClick={() => navigate('/fault-tree-report')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/fault-tree-report') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-sitemap w-4 h-4 mr-2"></i>
                <span>Fault Tree Report</span>
              </button>
              <button
                onClick={() => navigate('/residual-risk-risk-benefit')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/residual-risk-risk-benefit') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-balance-scale w-4 h-4 mr-2"></i>
                <span>Residual Risk & Risk-Benefit</span>
              </button>
              <button
                onClick={() => navigate('/risk-traceability-matrix')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/risk-traceability-matrix') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-project-diagram w-4 h-4 mr-2"></i>
                <span>Risk Traceability Matrix</span>
              </button>
              <button
                onClick={() => navigate('/risk-management-plan')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/risk-management-plan') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-clipboard-list w-4 h-4 mr-2"></i>
                <span>Risk Management Plan</span>
              </button>
              <button
                onClick={() => navigate('/risk-management-report')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/risk-management-report') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-chart-bar w-4 h-4 mr-2"></i>
                <span>Risk Management Report</span>
              </button>
            </div>
          )}
        </div>

        {/* Template Management */}
        <div className="mb-6">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-3">
            Templates
          </h3>
          <button
            onClick={() => navigate('/template-management')}
            className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
              isActiveRoute('/template-management') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
            }`}
          >
            <i className="fa-solid fa-file-word w-4 h-4 mr-2"></i>
            <span>Template Management</span>
          </button>
        </div>

        {/* Design Control Section */}
        <div>
          <button 
            onClick={() => setExpandedDesignControl(!expandedDesignControl)}
            className="flex items-center justify-between w-full text-left px-3 py-2 rounded-md text-gray-300 hover:bg-gray-700 transition-colors"
          >
            <div className="flex items-center">
              <i className="fa-solid fa-cogs w-5 h-5 mr-3"></i>
              <span>Design Control</span>
            </div>
            <i className={`fa-solid fa-chevron-down text-xs transition-transform duration-200 ${
              expandedDesignControl ? 'rotate-180' : ''
            }`}></i>
          </button>
          {expandedDesignControl && (
            <div className="ml-8 mt-2 space-y-1">
              <button className="flex items-center w-full text-left px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700">
                <i className="fa-regular fa-file-lines w-4 h-4 mr-2"></i>
                <span>User Need</span>
              </button>
              <button className="flex items-center w-full text-left px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700">
                <i className="fa-regular fa-file-lines w-4 h-4 mr-2"></i>
                <span>Design Input</span>
              </button>
              <button className="flex items-center w-full text-left px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700">
                <i className="fa-regular fa-file-lines w-4 h-4 mr-2"></i>
                <span>Design Output</span>
              </button>
              <button className="flex items-center w-full text-left px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700">
                <i className="fa-regular fa-file-lines w-4 h-4 mr-2"></i>
                <span>Verification</span>
              </button>
              <button className="flex items-center w-full text-left px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700">
                <i className="fa-regular fa-file-lines w-4 h-4 mr-2"></i>
                <span>Validation</span>
              </button>
            </div>
          )}
        </div>

        {/* Quality Management Section */}
        <div>
          <button 
            onClick={() => setExpandedQualityManagement(!expandedQualityManagement)}
            className="flex items-center justify-between w-full text-left px-3 py-2 rounded-md text-gray-300 hover:bg-gray-700 transition-colors"
          >
            <div className="flex items-center">
              <i className="fa-solid fa-award w-5 h-5 mr-3"></i>
              <span>Quality Management</span>
            </div>
            <i className={`fa-solid fa-chevron-down text-xs transition-transform duration-200 ${
              expandedQualityManagement ? 'rotate-180' : ''
            }`}></i>
          </button>
          {expandedQualityManagement && (
            <div className="ml-8 mt-2 space-y-1">
              <button 
                onClick={() => navigate('/capa')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/capa') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-check-double w-4 h-4 mr-2"></i>
                <span>CAPA</span>
              </button>
              <button 
                onClick={() => navigate('/change-control')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/change-control') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-arrows-rotate w-4 h-4 mr-2"></i>
                <span>Change Control</span>
              </button>
              <button 
                onClick={() => navigate('/non-conformance')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/non-conformance') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-triangle-exclamation w-4 h-4 mr-2"></i>
                <span>Non-Conformance</span>
              </button>
              <button 
                onClick={() => navigate('/export')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/export') ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'
                }`}
              >
                <i className="fa-solid fa-file-export w-4 h-4 mr-2"></i>
                <span>Export</span>
              </button>
            </div>
          )}
        </div>

        {/* Tools Section */}
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-3">TOOLS</h3>
          <ul className="space-y-1">
            <li>
              <button 
                onClick={() => navigate('/traceability-matrix')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${getActiveClass('/traceability-matrix')}`}
              >
                <i className="fa-solid fa-table w-5 h-5 mr-3"></i>
                <span>Traceability Matrix</span>
              </button>
            </li>
            <li>
              <button 
                onClick={() => navigate('/help')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${getActiveClass('/help')}`}
              >
                <i className="fa-solid fa-question-circle w-5 h-5 mr-3"></i>
                <span>Help</span>
              </button>
            </li>
            <li>
              <button 
                onClick={() => navigate('/admin')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${getActiveClass('/admin')}`}
              >
                <i className="fa-solid fa-user-shield w-5 h-5 mr-3"></i>
                <span>Admin</span>
              </button>
            </li>
          </ul>
        </div>
      </div>

      {/* Project Data Viewer Modal */}
      {showProjectDataViewer && selectedProjectForViewer && (
        <ErrorBoundary>
          <ProjectDataViewer
            selectedProject={selectedProjectForViewer}
            onClose={() => {
              setShowProjectDataViewer(false);
              setSelectedProjectForViewer(null);
            }}
          />
        </ErrorBoundary>
      )}

      {/* User Profile Modal */}
      <UserProfileModal
        isOpen={showUserProfileModal}
        onClose={handleCloseUserProfile}
        onLogout={handleLogout}
      />

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={showCreateProjectModal}
        onClose={handleCloseCreateProject}
        onProjectCreated={handleProjectCreated}
      />

      {/* Delete Project Modal */}
      <DeleteProjectModal
        isOpen={showDeleteProjectModal}
        onClose={() => setShowDeleteProjectModal(false)}
        onProjectDeleted={(projectId) => {
          // TODO: Implement actual project deletion logic
          console.log('Delete project confirmed:', projectId);
          setShowDeleteProjectModal(false);
        }}
        project={selectedProjectForDeletion}
      />
    </aside>
  );
};

export default DashboardSidebar; 