import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';

/**
 * Landing behavior:
 * - If a project is selected (persisted in localStorage), go straight to Mission Control.
 * - Otherwise, send the user to Projects to pick/create one.
 */
export default function LandingPage() {
  const navigate = useNavigate();
  const { currentProject } = useProject();

  useEffect(() => {
    const pid = currentProject?.id;
    if (pid) {
      navigate(`/projects/${pid}/dashboard`, { replace: true });
    } else {
      navigate('/projects', { replace: true });
    }
  }, [currentProject?.id, navigate]);

  return null;
}

