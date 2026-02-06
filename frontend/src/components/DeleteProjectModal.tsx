import React, { useState } from 'react';
import './DeleteProjectModal.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

interface Project {
  id: number;
  name: string;
  description?: string;
}

interface DeleteProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onProjectDeleted: (projectId: number) => void;
  project: Project | null;
}

const DeleteProjectModal: React.FC<DeleteProjectModalProps> = ({ 
  isOpen, 
  onClose, 
  onProjectDeleted,
  project
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDelete = async () => {
    if (!project) return;
    
    setIsLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        setError('Authentication required. Please log in again.');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/projects/${project.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        onProjectDeleted(project.id);
        onClose();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to delete project. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setError('');
    onClose();
  };

  if (!isOpen || !project) return null;

  return (
    <div className="delete-project-modal-overlay" onClick={onClose}>
      <div className="delete-project-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Delete Project</h2>
          <button className="close-button" onClick={onClose}>
            <i className="fa-solid fa-times"></i>
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="modal-content">
          <div className="warning-section">
            <div className="warning-icon">
              <i className="fa-solid fa-exclamation-triangle"></i>
            </div>
            <h3>Are you sure you want to delete this project?</h3>
            <p className="warning-text">
              This action cannot be undone. All project data including FMEA entries, CAPA records, 
              Change Controls, and Non-Conformances will be permanently deleted.
            </p>
          </div>

          <div className="project-info">
            <h4>Project Details:</h4>
            <div className="project-details">
              <div className="detail-item">
                <strong>Name:</strong> {project.name}
              </div>
              {project.description && (
                <div className="detail-item">
                  <strong>Description:</strong> {project.description}
                </div>
              )}
              <div className="detail-item">
                <strong>ID:</strong> {project.id}
              </div>
            </div>
          </div>

          <div className="modal-actions">
            <button
              type="button"
              onClick={handleCancel}
              disabled={isLoading}
              className="cancel-button"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleDelete}
              disabled={isLoading}
              className="delete-button"
            >
              {isLoading ? (
                <>
                  <i className="fa-solid fa-spinner fa-spin mr-2"></i>
                  Deleting...
                </>
              ) : (
                <>
                  <i className="fa-solid fa-trash mr-2"></i>
                  Delete Project
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeleteProjectModal; 