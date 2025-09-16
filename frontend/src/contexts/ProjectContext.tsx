import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Project } from '../services/apiService';

interface ProjectContextType {
  currentProject: Project | null;
  setCurrentProject: (project: Project | null) => void;
  isProjectSelected: boolean;
  clearCurrentProject: () => void;
  updateCurrentProject: (updates: Partial<Project>) => void;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

interface ProjectProviderProps {
  children: ReactNode;
}

export const ProjectProvider: React.FC<ProjectProviderProps> = ({ children }) => {
  const [currentProject, setCurrentProjectState] = useState<Project | null>(null);

  // Load current project from localStorage on component mount
  useEffect(() => {
    const savedProject = localStorage.getItem('currentProject');
    if (savedProject) {
      try {
        const parsedProject = JSON.parse(savedProject);
        setCurrentProjectState(parsedProject);
      } catch (error) {
        console.error('Failed to parse saved project:', error);
        localStorage.removeItem('currentProject');
      }
    }
  }, []);

  // Save current project to localStorage whenever it changes
  const setCurrentProject = (project: Project | null) => {
    setCurrentProjectState(project);
    if (project) {
      localStorage.setItem('currentProject', JSON.stringify(project));
    } else {
      localStorage.removeItem('currentProject');
    }
  };

  // Clear current project
  const clearCurrentProject = () => {
    setCurrentProjectState(null);
    localStorage.removeItem('currentProject');
  };

  // Update current project with partial updates
  const updateCurrentProject = (updates: Partial<Project>) => {
    if (currentProject) {
      const updatedProject = { ...currentProject, ...updates };
      setCurrentProject(updatedProject);
    }
  };

  const value: ProjectContextType = {
    currentProject,
    setCurrentProject,
    isProjectSelected: !!currentProject,
    clearCurrentProject,
    updateCurrentProject,
  };

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  );
};

export const useProject = (): ProjectContextType => {
  const context = useContext(ProjectContext);
  if (context === undefined) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
};
