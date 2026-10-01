import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import { useAuth } from '../contexts/AuthContext';
import { isProPlan } from '../config/features';
import api, { customerAuthEnabled } from '../axios';

/**
 * Landing behavior:
 * - Lite: redirect to /dfmea (standalone FMEA — no projects).
 * - Pro: If any projects exist, open Mission Control for selected/most recent.
 *        If none, create starter project and open Project Setup Wizard.
 */
export default function LandingPage() {
  const navigate = useNavigate();
  const { user, isLoading } = useAuth();
  const { currentProject, setCurrentProject, clearCurrentProject } = useProject();
  const ranRef = useRef(false);
  const [chooseProject, setChooseProject] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const start = async (sample: boolean) => {
    setBusy(true); setError('');
    try {
      const { data } = sample ? await api.post('/projects/sample') : await api.post('/projects', { name: 'FMEA-1', description: '' });
      setCurrentProject(data);
      navigate(`/projects/${data.id}/${sample ? 'fmea' : 'setup'}`, { replace: true });
    } catch (err: any) {
      setError(typeof err?.response?.data?.detail === 'string' ? err.response.data.detail : 'Unable to create your project. Please try again.');
      setBusy(false);
    }
  };

  const plan = user?.plan ?? 'lite';
  const isPro = isProPlan(plan);

  useEffect(() => {
    if (isLoading || !user) return;
    if (ranRef.current) return;
    ranRef.current = true;

    (async () => {
      try {
        // Lite plan: no projects — go to standalone FMEA
        if (!isPro) {
          navigate(customerAuthEnabled ? '/billing' : '/dfmea', { replace: true });
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
          setChooseProject(true);
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
  }, [clearCurrentProject, currentProject?.id, isLoading, isPro, navigate, setCurrentProject, user]);

  if (chooseProject) return <section className="max-w-2xl mx-auto p-8 space-y-5">
    <h1 className="text-3xl font-semibold">Start your first project</h1>
    <p>Explore an editable sample FMEA or start with your own project. The sample counts toward your project allowance. Your saved work carries into Team when you upgrade.</p>
    <p>The sample is fictional training data and needs review before use.</p>
    {error && <p role="alert" className="text-red-700">{error}</p>}
    <div className="flex flex-wrap gap-3">
      <button disabled={busy} onClick={() => void start(true)} className="rounded bg-blue-700 text-white p-3 disabled:opacity-50">Explore sample project</button>
      <button disabled={busy} onClick={() => void start(false)} className="rounded border p-3 disabled:opacity-50">Create my own project</button>
    </div>
  </section>;
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-primary">
      <div className="flex flex-col items-center gap-3">
        <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full" />
        <p className="text-text-secondary text-sm">Loading…</p>
      </div>
    </div>
  );
}
