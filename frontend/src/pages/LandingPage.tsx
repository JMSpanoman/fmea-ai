import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import api from '../axios';

/**
 * Landing behavior:
 * - If any projects exist: open Mission Control for the selected (or most recent) project.
 * - If no projects exist yet: create a starter project and open the Project Setup Wizard.
 */
export default function LandingPage() {
  const navigate = useNavigate();
  const { currentProject, setCurrentProject, clearCurrentProject } = useProject();
  const ranRef = useRef(false);

  useEffect(() => {
    if (ranRef.current) return;
    ranRef.current = true;

    (async () => {
      try {
        // 1) If a project is already selected (persisted), verify it still exists for this user.
        const pid = currentProject?.id;
        if (pid) {
          try {
            await api.get(`/projects/${pid}`);
            navigate(`/projects/${pid}/dashboard`, { replace: true });
            return;
          } catch (e: any) {
            if (e?.response?.status === 404) {
              clearCurrentProject();
            } else {
              // For non-404 errors, continue to list-based selection.
            }
          }
        }

        // 2) Fetch projects for this user
        const res = await api.get('/projects');
        const projects = Array.isArray(res.data) ? res.data : [];

        // 3) If none exist, create one and go to setup wizard
        if (!projects.length) {
          const created = await api.post('/projects', {
            name: 'FMEA-1',
            description: 'Starter project created automatically. Complete Project Setup to begin.',
          });
          const p = created?.data;
          if (p?.id) {
            setCurrentProject(p);
            navigate(`/projects/${p.id}/setup`, { replace: true });
            return;
          }
          // Fallback if response shape is unexpected
          navigate('/projects', { replace: true });
          return;
        }

        // 4) Otherwise, pick the most recently created project and open Mission Control
        const sorted = projects
          .slice()
          .sort((a: any, b: any) => String(b?.created_at || '').localeCompare(String(a?.created_at || '')));
        const picked = sorted[0];
        if (picked?.id) {
          setCurrentProject(picked);
          navigate(`/projects/${picked.id}/dashboard`, { replace: true });
          return;
        }

        navigate('/projects', { replace: true });
      } catch {
        // Conservative fallback
        navigate('/projects', { replace: true });
      }
    })();
  }, [clearCurrentProject, currentProject?.id, navigate, setCurrentProject]);

  return null;
}

