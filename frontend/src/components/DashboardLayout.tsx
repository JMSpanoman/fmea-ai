import React, { useState } from 'react';
import { Project } from '../services/apiService';
import DashboardSidebar from './DashboardSidebar';

interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ 
  children, 
  title = "Dashboard",
  subtitle 
}) => {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const handleProjectSelect = (project: Project) => {
    setSelectedProject(project);
  };

  return (
    <div className="flex h-screen bg-gray-200">
      {/* Sidebar */}
      <DashboardSidebar
        onProjectSelect={handleProjectSelect}
        selectedProjectId={selectedProject?.id}
        selectedProject={selectedProject || undefined}
      />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-gray-200 shadow-sm border-b border-gray-300 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                {title}
              </h1>
              {subtitle && (
                <p className="text-sm text-gray-500 mt-1">
                  {subtitle}
                </p>
              )}
              {selectedProject && (
                <div className="flex items-center mt-2">
                  <span className="text-sm text-gray-500">Active Project:</span>
                  <span className="text-sm font-medium text-gray-900 ml-2">
                    {selectedProject.name}
                  </span>
                </div>
              )}
            </div>
            <div className="flex items-center space-x-4">
              {selectedProject && (
                <span className="text-sm text-gray-500">
                  Last updated: {new Date(selectedProject.updated_at || selectedProject.created_at).toLocaleDateString()}
                </span>
              )}
              <button className="text-gray-500 hover:text-gray-700">
                <i className="fa-solid fa-bell"></i>
              </button>
              <div className="relative">
                <button className="flex items-center text-gray-700 hover:text-gray-900">
                  <img src="https://storage.googleapis.com/uxpilot-auth.appspot.com/avatars/avatar-3.jpg" alt="User" className="w-8 h-8 rounded-full mr-2" />
                  <span className="font-medium">John Spanomanolis</span>
                  <i className="fa-solid fa-chevron-down ml-2 text-xs"></i>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto">
          {selectedProject ? (
            children
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Project Selected</h3>
                <p className="text-gray-500">
                  Select a project from the sidebar to get started
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout; 