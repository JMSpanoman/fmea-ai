import React, { useState } from 'react';
import ProjectsSidebar from './ProjectsSidebar';
import Footer from './Footer';

interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const handleProjectSelect = (project: Project) => {
    setSelectedProject(project);
  };

  return (
    <div className="flex h-screen bg-gray-200">
      {/* Projects Sidebar */}
      <ProjectsSidebar
        onProjectSelect={handleProjectSelect}
        selectedProjectId={selectedProject?.id}
      />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-gray-200 shadow-sm border-b border-gray-300 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                {selectedProject ? selectedProject.name : 'Select a Project'}
              </h1>
              {selectedProject && (
                <p className="text-sm text-gray-500 mt-1">
                  {selectedProject.description}
                </p>
              )}
            </div>
            <div className="flex items-center space-x-4">
              {selectedProject && (
                <span className="text-sm text-gray-500">
                  Last updated: {new Date(selectedProject.updated_at).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto p-6">
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
        
        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
};

export default MainLayout; 