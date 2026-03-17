import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import { useAuth } from '../contexts/AuthContext';
import { isProPlan } from '../config/features';
import api from '../axios';

/**
 * Landing behavior:
 * - Lite: redirect to /dfmea (standalone FMEA — no projects).
 * - Pro: If any projects exist, open Mission Control for selected/most recent.
 *        If none, create starter project and open Project Setup Wizard.
 */
export default function LandingPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { currentProject, setCurrentProject, clearCurrentProject } = useProject();
  const ranRef = useRef(false);

  const plan = user?.plan ?? 'lite';
  const isPro = isProPlan(plan);

  useEffect(() => {
    if (ranRef.current) return;
    ranRef.current = true;

    (async () => {
      try {
        // Lite plan: no projects — go to standalone FMEA
        if (!isPro) {
          navigate('/dfmea', { replace: true });
          return;
        }

        // Pro: project-based flow
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
          navigate('/projects', { replace: true });
          return;
        }

        // 4) Pick the most recently created project and open Mission Control
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
        navigate(isPro ? '/projects' : '/dfmea', { replace: true });
      }
    })();
  }, [clearCurrentProject, currentProject?.id, isPro, navigate, setCurrentProject]);

  return null;
}

