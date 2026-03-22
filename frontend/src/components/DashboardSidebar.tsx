import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { getProjects, Project } from '../services/apiService';
import authService from '../services/authService';
import ProjectDataViewer from './ProjectDataViewer';
import ErrorBoundary from './ErrorBoundary';
import UserProfileModal from './UserProfileModal';
import CreateProjectModal from './CreateProjectModal';
import DeleteProjectModal from './DeleteProjectModal';
import GenerateDesignInputsModal from './GenerateDesignInputsModal';
import GenerateDesignOutputsModal from './GenerateDesignOutputsModal';

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
  const [expandedSmartQSRisk, setExpandedSmartQSRisk] = useState(false);
  const [expandedSmartQSDesign, setExpandedSmartQSDesign] = useState(false);
  const [expandedSmartQSInsight, setExpandedSmartQSInsight] = useState(false);
  const [showGenerateDesignInputsModal, setShowGenerateDesignInputsModal] = useState(false);
  const [showGenerateDesignOutputsModal, setShowGenerateDesignOutputsModal] = useState(false);
  const [expandedSmartQSGovernance, setExpandedSmartQSGovernance] = useState(false);
  const [expandedSmartQSPostMarket, setExpandedSmartQSPostMarket] = useState(false);
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
    // Immediately route into the Setup Wizard for the new project
    if (newProject?.id) {
      navigate(`/projects/${newProject.id}/setup`);
    }
  };

  return (
    <aside className="w-64 bg-gray-200 text-gray-900 h-screen overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b border-gray-300">
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
        <div className="flex items-center space-x-3 p-3 bg-gray-100 rounded-lg">
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
            <p className="text-sm font-medium text-gray-900 truncate">
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
            <p className="text-xs text-gray-600 truncate">
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
            className="text-gray-600 hover:text-gray-900 transition-colors"
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
          <h3 className="text-sm font-semibold text-gray-600">CURRENT PROJECT</h3>
          <button className="text-gray-600 hover:text-gray-900">
            <i className="fa-solid fa-cog text-sm"></i>
          </button>
        </div>
        <div className="bg-gray-100 rounded-md p-2 flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span className="font-medium">
              {selectedProject ? selectedProject.name : 'No Project Selected'}
            </span>
          </div>
          <button 
            onClick={toggleProjectsExpansion}
            className="text-gray-600 hover:text-gray-900 transition-transform duration-200"
            style={{ transform: expandedProjects ? 'rotate(180deg)' : 'rotate(0deg)' }}
          >
            <i className="fa-solid fa-chevron-down text-xs"></i>
          </button>
        </div>
        {selectedProject && (
          <div className="text-xs text-gray-600 mt-1 text-center">
            Click any project to view its data
          </div>
        )}
        
        {/* Expandable Projects Section */}
        {expandedProjects && (
          <div className="mt-3 bg-gray-100 rounded-md p-3">
            {/* Create New Project Button */}
            <button
              onClick={handleOpenCreateProject}
              className="w-full bg-green-600 hover:bg-green-700 text-black text-sm py-2 px-3 rounded-md transition-colors flex items-center justify-center mb-3"
            >
              <i className="fa-solid fa-plus mr-2"></i>
              Create New Project
            </button>
            
            {loading ? (
              <div className="text-center text-gray-900 text-sm">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400 mx-auto mb-2"></div>
                Loading projects...
              </div>
            ) : error ? (
              <div className="text-red-400 text-sm">{error}</div>
            ) : projects.length === 0 ? (
              <div className="text-center">
                <div className="text-gray-900 text-sm mb-3">No projects available</div>
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
                        : 'hover:bg-blue-100 text-gray-700'
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
        <i className="fa-solid fa-search absolute left-3 top-2.5 text-gray-600"></i>
        <input 
          type="text" 
          placeholder="Search..." 
          className="w-full bg-white rounded-md pl-10 pr-4 py-2 text-sm border border-gray-300 focus:outline-none focus:border-blue-500" 
        />
      </div>

      {/* Navigation Sections */}
      <div className="p-4 space-y-4">
        {/* SmartQS Header */}
        <div className="mb-4">
          <h2 className="text-lg font-bold text-gray-900 mb-4 px-3">SmartQS</h2>
        </div>

        {/* SmartQS Risk */}
        <div>
          <button 
            onClick={() => setExpandedSmartQSRisk(!expandedSmartQSRisk)}
            className="flex items-center justify-between w-full text-left px-3 py-2 rounded-md text-gray-900 hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center">
              <i className="fa-solid fa-shield-halved w-5 h-5 mr-3"></i>
              <span>SmartQS: Risk</span>
            </div>
            <i className={`fa-solid fa-chevron-down text-xs transition-transform duration-200 ${
              expandedSmartQSRisk ? 'rotate-180' : ''
            }`}></i>
          </button>
          {expandedSmartQSRisk && (
            <div className="ml-8 mt-2 space-y-1">
              <button 
                onClick={() => navigate('/builder')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/builder') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-shield-halved w-4 h-4 mr-2"></i>
                <span>FMEA</span>
              </button>
              <button 
                onClick={() => navigate('/hazard-analysis')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/hazard-analysis') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-exclamation-triangle w-4 h-4 mr-2"></i>
                <span>Hazard Analysis</span>
              </button>
              <button
                onClick={() => {
                  const projectId = selectedProject?.id;
                  if (projectId) navigate(`/projects/${projectId}/device-architecture`);
                  else alert('Select a project first');
                }}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  location.pathname.includes('/device-architecture') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-sitemap w-4 h-4 mr-2"></i>
                <span>Device Architecture (SmartRisk)</span>
              </button>
              <button 
                onClick={() => navigate('/risk-management-plan')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/risk-management-plan') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-clipboard-list w-4 h-4 mr-2"></i>
                <span>Risk Management Plan</span>
              </button>
              <button 
                onClick={() => navigate('/risk-evaluation-report')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/risk-evaluation-report') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-chart-line w-4 h-4 mr-2"></i>
                <span>Risk Evaluation Report</span>
              </button>
              <button 
                onClick={() => navigate('/risk-control-implementation')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/risk-control-implementation') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-shield-check w-4 h-4 mr-2"></i>
                <span>Risk Control Implementation</span>
              </button>
              <button 
                onClick={() => navigate('/fault-tree-report')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/fault-tree-report') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-sitemap w-4 h-4 mr-2"></i>
                <span>Fault Tree Report</span>
              </button>
              <button
                onClick={() => navigate('/residual-risk-risk-benefit')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/residual-risk-risk-benefit') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-balance-scale w-4 h-4 mr-2"></i>
                <span>Residual Risk & Risk-Benefit</span>
              </button>
              <button
                onClick={() => navigate('/risk-traceability-matrix')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/risk-traceability-matrix') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-project-diagram w-4 h-4 mr-2"></i>
                <span>Risk Traceability Matrix</span>
              </button>
              <button 
                onClick={() => navigate('/capa')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/capa') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-check-double w-4 h-4 mr-2"></i>
                <span>CAPA</span>
              </button>
              <button 
                onClick={() => navigate('/pms')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/pms') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-chart-area w-4 h-4 mr-2"></i>
                <span>PMS</span>
              </button>
            </div>
          )}
        </div>

        {/* SmartQS Design */}
        <div>
          <button 
            onClick={() => setExpandedSmartQSDesign(!expandedSmartQSDesign)}
            className="flex items-center justify-between w-full text-left px-3 py-2 rounded-md text-gray-900 hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center">
              <i className="fa-solid fa-cogs w-5 h-5 mr-3"></i>
              <span>SmartQS Design</span>
            </div>
            <i className={`fa-solid fa-chevron-down text-xs transition-transform duration-200 ${
              expandedSmartQSDesign ? 'rotate-180' : ''
            }`}></i>
          </button>
          {expandedSmartQSDesign && (
            <div className="ml-8 mt-2 space-y-1">
              <button 
                onClick={() => {
                  console.log('Design Inputs button clicked');
                  setShowGenerateDesignInputsModal(true);
                }}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/design-inputs') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-arrow-right-to-bracket w-4 h-4 mr-2"></i>
                <span>Design Inputs</span>
              </button>
              <button 
                onClick={() => {
                  console.log('Design Outputs button clicked');
                  setShowGenerateDesignOutputsModal(true);
                }}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/design-outputs') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-arrow-right-from-bracket w-4 h-4 mr-2"></i>
                <span>Design Outputs</span>
              </button>
              <button 
                onClick={() => {
                  const projectId = selectedProject?.id;
                  if (projectId) {
                    navigate(`/projects/${projectId}/vv-tests`);
                  } else {
                    navigate('/vv-tests');
                  }
                }}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/vv-tests') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-check-circle w-4 h-4 mr-2"></i>
                <span>V&V Tests</span>
              </button>
              <button 
                onClick={() => navigate('/traceability-matrix')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/traceability-matrix') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-table w-4 h-4 mr-2"></i>
                <span>Traceability Matrix</span>
              </button>
            </div>
          )}
        </div>

        {/* SmartQS Change */}
        <div>
          <button 
            onClick={() => navigate('/change-control')}
            className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${
              isActiveRoute('/change-control') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
            }`}
          >
            <i className="fa-solid fa-arrows-rotate w-5 h-5 mr-3"></i>
            <span>SmartQS Change</span>
          </button>
        </div>

        {/* SmartQS Insight */}
        <div>
          <button 
            onClick={() => setExpandedSmartQSInsight(!expandedSmartQSInsight)}
            className="flex items-center justify-between w-full text-left px-3 py-2 rounded-md text-gray-900 hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center">
              <i className="fa-solid fa-chart-line w-5 h-5 mr-3"></i>
              <span>SmartQS Insight</span>
            </div>
            <i className={`fa-solid fa-chevron-down text-xs transition-transform duration-200 ${
              expandedSmartQSInsight ? 'rotate-180' : ''
            }`}></i>
          </button>
          {expandedSmartQSInsight && (
            <div className="ml-8 mt-2 space-y-1">
              <button 
                onClick={() => navigate('/dashboard')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/dashboard') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-chart-line w-4 h-4 mr-2"></i>
                <span>Dashboard</span>
              </button>
              <button 
                onClick={() => navigate('/risk-management-report')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/risk-management-report') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-chart-bar w-4 h-4 mr-2"></i>
                <span>Risk Management Report</span>
              </button>
              <button 
                onClick={() => navigate('/libraries/hazards')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  location.pathname.startsWith('/libraries') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-book w-4 h-4 mr-2"></i>
                <span>Risk Knowledge Base (Libraries)</span>
              </button>
              <button 
                onClick={() => navigate('/export')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/export') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-file-export w-4 h-4 mr-2"></i>
                <span>Export</span>
              </button>
            </div>
          )}
        </div>

        {/* SmartQS Governance */}
        <div>
          <button 
            onClick={() => setExpandedSmartQSGovernance(!expandedSmartQSGovernance)}
            className="flex items-center justify-between w-full text-left px-3 py-2 rounded-md text-gray-900 hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center">
              <i className="fa-solid fa-gavel w-5 h-5 mr-3"></i>
              <span>SmartQS Governance</span>
            </div>
            <i className={`fa-solid fa-chevron-down text-xs transition-transform duration-200 ${
              expandedSmartQSGovernance ? 'rotate-180' : ''
            }`}></i>
          </button>
          {expandedSmartQSGovernance && (
            <div className="ml-8 mt-2 space-y-1">
              <button 
                onClick={() => navigate('/documents')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/documents') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-file-lines w-4 h-4 mr-2"></i>
                <span>Documents</span>
              </button>
              <button 
                onClick={() => navigate('/training')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/training') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-graduation-cap w-4 h-4 mr-2"></i>
                <span>Training</span>
              </button>
              <button 
                onClick={() => navigate('/audits')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/audits') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-clipboard-check w-4 h-4 mr-2"></i>
                <span>Audits</span>
              </button>
              <button 
                onClick={() => navigate('/suppliers')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/suppliers') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-industry w-4 h-4 mr-2"></i>
                <span>Suppliers</span>
              </button>
              <button 
                onClick={() => navigate('/ncrs')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/ncrs') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-triangle-exclamation w-4 h-4 mr-2"></i>
                <span>NCRs</span>
              </button>
              <button 
                onClick={() => navigate('/equipment')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/equipment') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-wrench w-4 h-4 mr-2"></i>
                <span>Equipment</span>
              </button>
              <button
                onClick={() => navigate('/template-management')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/template-management') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-file-word w-4 h-4 mr-2"></i>
                <span>Template Management</span>
              </button>
            </div>
          )}
        </div>

        {/* SmartQS Post Market */}
        <div>
          <button 
            onClick={() => setExpandedSmartQSPostMarket(!expandedSmartQSPostMarket)}
            className="flex items-center justify-between w-full text-left px-3 py-2 rounded-md text-gray-900 hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center">
              <i className="fa-solid fa-chart-area w-5 h-5 mr-3"></i>
              <span>SmartQS Post Market</span>
            </div>
            <i className={`fa-solid fa-chevron-down text-xs transition-transform duration-200 ${
              expandedSmartQSPostMarket ? 'rotate-180' : ''
            }`}></i>
          </button>
          {expandedSmartQSPostMarket && (
            <div className="ml-8 mt-2 space-y-1">
              <button 
                onClick={() => navigate('/post-market')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/post-market') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-chart-line w-4 h-4 mr-2"></i>
                <span>Post-Market Surveillance</span>
              </button>
              <button
                onClick={() => {
                  const pid = selectedProject?.id;
                  if (pid) navigate(`/projects/${pid}/pms/plan-generator`);
                  else navigate('/projects');
                }}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  location.pathname.includes('/pms/plan-generator') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-file-medical w-4 h-4 mr-2"></i>
                <span>PMS plan generator</span>
              </button>
              <button 
                onClick={() => navigate('/complaints')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isActiveRoute('/complaints') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-comment-dots w-4 h-4 mr-2"></i>
                <span>Complaints</span>
              </button>
            </div>
          )}
        </div>

        {/* Help & Admin */}
        <div className="mt-6 pt-4 border-t border-gray-300">
          <ul className="space-y-1">
            <li>
              <button 
                onClick={() => navigate('/help')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${
                  isActiveRoute('/help') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <i className="fa-solid fa-question-circle w-5 h-5 mr-3"></i>
                <span>Help</span>
              </button>
            </li>
            <li>
              <button 
                onClick={() => navigate('/admin')}
                className={`flex items-center w-full text-left px-3 py-2 rounded-md transition-colors ${
                  isActiveRoute('/admin') ? 'bg-blue-600 text-white' : 'text-gray-900 hover:bg-gray-100'
                }`}
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

      {/* Generate Design Inputs Modal */}
      <GenerateDesignInputsModal
        isOpen={showGenerateDesignInputsModal}
        onClose={() => {
          console.log('Closing modal');
          setShowGenerateDesignInputsModal(false);
        }}
        onDesignInputsGenerated={(designInputs) => {
          console.log('Generated design inputs:', designInputs);
          // Optionally navigate to a page showing the generated inputs
        }}
      />

      {/* Generate Design Outputs Modal */}
      <GenerateDesignOutputsModal
        isOpen={showGenerateDesignOutputsModal}
        onClose={() => {
          console.log('Closing Design Outputs modal');
          setShowGenerateDesignOutputsModal(false);
        }}
        onDesignOutputsGenerated={(designOutputs) => {
          console.log('Generated design outputs:', designOutputs);
          // Optionally navigate to a page showing the generated outputs
        }}
      />
    </aside>
  );
};

export default DashboardSidebar; 