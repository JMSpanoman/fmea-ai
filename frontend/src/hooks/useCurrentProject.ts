import { useProject } from '../contexts/ProjectContext';

/**
 * Custom hook for easy access to current project functionality
 * Provides current project, project selection status, and utility functions
 */
export const useCurrentProject = () => {
  const { currentProject, setCurrentProject, isProjectSelected, clearCurrentProject, updateCurrentProject } = useProject();

  /**
   * Check if a project is currently selected
   */
  const hasProject = () => isProjectSelected;

  /**
   * Get the current project ID
   */
  const getProjectId = () => currentProject?.id;

  /**
   * Get the current project name
   */
  const getProjectName = () => currentProject?.name;

  /**
   * Get the current project status
   */
  const getProjectStatus = () => currentProject?.status;

  /**
   * Check if the current project is in draft status
   */
  const isProjectDraft = () => currentProject?.status === 'draft';

  /**
   * Check if the current project is in final status
   */
  const isProjectFinal = () => currentProject?.status === 'final';

  /**
   * Check if the current project is in exported status
   */
  const isProjectExported = () => currentProject?.status === 'exported';

  /**
   * Get project creation date
   */
  const getProjectCreatedDate = () => currentProject?.created_at;

  /**
   * Get project last updated date
   */
  const getProjectUpdatedDate = () => currentProject?.updated_at;

  /**
   * Get project description
   */
  const getProjectDescription = () => currentProject?.description;

  /**
   * Require project selection - throws error if no project is selected
   */
  const requireProject = () => {
    if (!isProjectSelected || !currentProject) {
      throw new Error('A project must be selected to perform this action');
    }
    return currentProject;
  };

  /**
   * Require project selection with custom error message
   */
  const requireProjectWithMessage = (message: string) => {
    if (!isProjectSelected || !currentProject) {
      throw new Error(message);
    }
    return currentProject;
  };

  /**
   * Check if project selection is required for an action
   */
  const isProjectRequired = () => isProjectSelected;

  /**
   * Get project selection warning message
   */
  const getProjectRequiredMessage = () => {
    if (isProjectSelected) {
      return null;
    }
    return 'Please select a project to continue';
  };

  /**
   * Get project context for API calls
   */
  const getProjectContext = () => {
    if (!currentProject) {
      return null;
    }
    return {
      projectId: currentProject.id,
      projectName: currentProject.name,
      projectStatus: currentProject.status
    };
  };

  return {
    // Core project data
    currentProject,
    isProjectSelected,
    
    // Utility functions
    hasProject,
    getProjectId,
    getProjectName,
    getProjectStatus,
    getProjectDescription,
    getProjectCreatedDate,
    getProjectUpdatedDate,
    
    // Status checks
    isProjectDraft,
    isProjectFinal,
    isProjectExported,
    
    // Project requirements
    requireProject,
    requireProjectWithMessage,
    isProjectRequired,
    getProjectRequiredMessage,
    
    // Context helpers
    getProjectContext,
    
    // Actions
    setCurrentProject,
    clearCurrentProject,
    updateCurrentProject
  };
};
