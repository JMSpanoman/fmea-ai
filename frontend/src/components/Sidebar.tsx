import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import { useAuth } from '../contexts/AuthContext';
import ProjectSelector from './ProjectSelector';

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentProject, isProjectSelected } = useProject();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Get user initials for avatar
  const getUserInitials = (email: string) => {
    return email.split('@')[0].substring(0, 2).toUpperCase();
  };

  const navItems = [
    { path: '/', label: 'Home', icon: 'fa-home', level: 1 },
    { path: '/projects', label: 'Projects', icon: 'fa-folder-tree', level: 1 },
    { path: '/dfmea', label: 'FMEA Generator', icon: 'fa-shield-halved', level: 2 },
    { path: '/dashboard', label: 'Dashboard', icon: 'fa-chart-line', level: 2 },
    { path: '/capa', label: 'CAPA', icon: 'fa-clipboard-check', level: 2 },
    { path: '/change-control', label: 'Change Control', icon: 'fa-arrows-rotate', level: 3 },
    { path: '/nonconformance', label: 'Non-Conformance', icon: 'fa-triangle-exclamation', level: 2 },
    { path: '/hazard-analysis', label: 'Hazard Analysis', icon: 'fa-exclamation-triangle', level: 3 },
    { path: '/fault-tree-report', label: 'Fault Tree', icon: 'fa-sitemap', level: 3 },
    { path: '/risk-management-report', label: 'Risk Management', icon: 'fa-shield-halved', level: 3 },
    { path: '/risk-management-plan', label: 'Risk Plan', icon: 'fa-clipboard-list', level: 2 },
    { path: '/traceability-matrix', label: 'Traceability', icon: 'fa-table', level: 2 },
    { path: '/residual-risk', label: 'Residual Risk', icon: 'fa-exclamation-circle', level: 3 },
    { path: '/risk-control-implementation', label: 'Risk Control', icon: 'fa-shield-alt', level: 3 },
    { path: '/risk-evaluation-report', label: 'Risk Eval', icon: 'fa-chart-bar', level: 3 },
    { path: '/mitigation', label: 'Mitigation', icon: 'fa-tools', level: 2 },
    { path: '/export', label: 'Export', icon: 'fa-download', level: 1 },
    { path: '/help', label: 'Help', icon: 'fa-question-circle', level: 1 }
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const getLevelColor = (level: number) => {
    switch (level) {
      case 1: return 'bg-green-100 text-green-800';
      case 2: return 'bg-yellow-100 text-yellow-800';
      case 3: return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getLevelLabel = (level: number) => {
    switch (level) {
      case 1: return 'Level 1';
      case 2: return 'Level 2';
      case 3: return 'Level 3';
      default: return 'Unknown';
    }
  };

  const canAccess = (itemLevel: number) => {
    // For now, allow all users to access all features
    // In a real app, you might have different access levels based on user roles
    return true;
  };

  return (
    <div className="w-64 bg-white shadow-lg h-screen fixed left-0 top-0 overflow-y-auto">
      {/* App Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center mb-3">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
            <i className="fa-solid fa-shield-halved text-blue-600 text-lg"></i>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Foton aiQMS</h2>
            <p className="text-sm text-gray-500">Quality Management System</p>
          </div>
        </div>
        
        {/* Current Project Info */}
        <div className="text-xs text-gray-500">
          <div className="flex items-center justify-between">
            <span>Active Project:</span>
            <span className="font-medium text-blue-600">
              {currentProject ? currentProject.name : 'No Project Selected'}
            </span>
          </div>
          {currentProject && (
            <div className="mt-1">
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                currentProject.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                currentProject.status === 'final' ? 'bg-green-100 text-green-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {currentProject.status || 'Unknown'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* User Profile Section */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
            {user ? getUserInitials(user.email) : 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-medium text-gray-900 truncate">
              {user ? user.email.split('@')[0] : 'User'}
            </h3>
            <p className="text-xs text-gray-500 truncate">
              {user ? user.email : 'Not logged in'}
            </p>
          </div>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="text-gray-400 hover:text-gray-600"
          >
            <i className="fa-solid fa-chevron-down text-xs"></i>
          </button>
        </div>
        

        {/* User Menu Dropdown */}
        {showUserMenu && (
          <div className="mt-3 p-3 bg-white rounded-lg border border-gray-200 shadow-sm">
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Email:</span>
                <span className="font-medium text-gray-900">{user?.email}</span>
              </div>
              <div className="pt-2 border-t border-gray-100">
                <button 
                  onClick={logout}
                  className="w-full text-left text-red-600 hover:text-red-800 text-xs"
                >
                  <i className="fa-solid fa-sign-out-alt mr-2"></i>
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Project Selector */}
      <div className="p-4 border-b border-gray-200">
        <ProjectSelector compact={true} showLabel={false} />
      </div>

      {/* Navigation Menu */}
      <nav className="p-4">
        <div className="space-y-1">
          {navItems.map((item) => {
            const accessible = canAccess(item.level);
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                disabled={!accessible}
                className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  !accessible 
                    ? 'text-gray-400 cursor-not-allowed opacity-50'
                    : isActive(item.path)
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-500'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
                title={!accessible ? `Requires ${getLevelLabel(item.level)} access` : item.label}
              >
                <i className={`${item.icon} w-5 text-center mr-3`}></i>
                <span className="flex-1 text-left">{item.label}</span>
                {item.level > 1 && (
                  <span className={`ml-2 inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium ${getLevelColor(item.level)}`}>
                    {item.level}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Quick Actions */}
      <div className="p-4 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Actions</h3>
        <div className="space-y-2">
          <button 
            onClick={() => navigate('/projects')}
            className="w-full flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md transition-colors"
          >
            <i className="fa-solid fa-plus w-5 text-center mr-3"></i>
            New Project
          </button>
          <button 
            onClick={() => navigate('/dashboard')}
            className="w-full flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md transition-colors"
          >
            <i className="fa-solid fa-chart-line w-5 text-center mr-3"></i>
            View Dashboard
          </button>
          <button 
            onClick={() => navigate('/export')}
            className="w-full flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md transition-colors"
          >
            <i className="fa-solid fa-download w-5 text-center mr-3"></i>
            Export Data
          </button>
        </div>
      </div>

      {/* System Info */}
      <div className="p-4 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-900 mb-3">System Info</h3>
        <div className="space-y-2 text-xs text-gray-600">
          <div className="flex justify-between">
            <span>Version:</span>
            <span className="font-medium">1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span>Environment:</span>
            <span>Development</span>
          </div>
          <div className="flex justify-between">
            <span>Last Updated:</span>
            <span>Today</span>
          </div>
          <div className="flex justify-between">
            <span>Status:</span>
            <span className="text-green-600 font-medium">Online</span>
          </div>
          <div className="flex justify-between">
            <span>User:</span>
            <span className="font-medium text-blue-600">
              {user ? user.email.split('@')[0] : 'Not logged in'}
            </span>
          </div>
          {currentProject && (
            <div className="flex justify-between">
              <span>Project:</span>
            <span className="font-medium text-blue-600">{currentProject.name}</span>
          </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar; 