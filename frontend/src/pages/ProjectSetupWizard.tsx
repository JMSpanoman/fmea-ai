import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  componentsApi,
  projectInitializeApi,
  projectInitializeFromProfileApi,
  projectProfileApi,
  projectsApi,
  ProjectProfile,
} from '../services/apiPhase1';
import { useProject } from '../contexts/ProjectContext';

type WizardStep = 1 | 2 | 3;

type ComponentDraft = {
  id?: string;
  name: string;
  description?: string;
};

const setupSkippedKey = (projectId: string) => `setup_skipped_${projectId}`;

function normalize(s: string | null | undefined) {
  return (s || '').trim();
}

function isProfileFilled(p: ProjectProfile) {
  return Boolean(
    normalize(p.intended_use) ||
      normalize(p.device_description) ||
      normalize(p.user_population) ||
      normalize(p.use_environment)
  );
}

export default function ProjectSetupWizard() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { clearCurrentProject } = useProject();

  const [step, setStep] = useState<WizardStep>(1);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [finished, setFinished] = useState(false);
  const [generatingDrafts, setGeneratingDrafts] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [profile, setProfile] = useState<ProjectProfile>({
    intended_use: '',
    device_description: '',
    user_population: '',
    use_environment: '',
  });
  const [components, setComponents] = useState<ComponentDraft[]>([{ name: '', description: '' }]);
  const [bulkText, setBulkText] = useState('');

  const validProjectId = projectId || '';

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!validProjectId) return;
      setLoading(true);
      setError(null);
      try {
        // Validate the project exists for the current user.
        // This prevents confusing "Project not found" errors when the URL/localStorage
        // contains a stale projectId after switching backends or redeploys.
        try {
          await projectsApi.getById(validProjectId);
        } catch (e: any) {
          const msg = String(e?.message || '');
          if (msg.toLowerCase().includes('project not found')) {
            try {
              clearCurrentProject();
            } catch {
              // ignore
            }
            if (!cancelled) {
              setError('Project not found. Please select or create a project again.');
              // Redirect back to project list to recover.
              navigate('/projects', { replace: true });
            }
            return;
          }
        }

        // Profile: 404 means "not set yet" (treat as empty)
        try {
          const p = await projectProfileApi.get(validProjectId);
          if (!cancelled) {
            setProfile({
              intended_use: p.intended_use || '',
              device_description: p.device_description || '',
              user_population: p.user_population || '',
              use_environment: p.use_environment || '',
              key_safety_characteristics: p.key_safety_characteristics || [],
            });
          }
        } catch (e: any) {
          // If profile doesn't exist yet, ignore.
        }

        const comps = await componentsApi.getByProject(validProjectId).catch(() => []);
        if (!cancelled) {
          if (Array.isArray(comps) && comps.length) {
            setComponents(
              comps.map((c: any) => ({
                id: c.id,
                name: c.name || '',
                description: c.description || '',
              }))
            );
          } else {
            setComponents([{ name: '', description: '' }]);
          }
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [validProjectId]);

  const componentCount = useMemo(
    () => components.filter((c) => normalize(c.name)).length,
    [components]
  );

  const canContinue = useMemo(() => {
    if (step === 1) return true; // allow empty; wizard can be skipped or filled later
    if (step === 2) return true; // allow empty components (we’ll warn on finish)
    return true;
  }, [step]);

  function goDashboard() {
    if (!validProjectId) return;
    navigate(`/projects/${validProjectId}/dashboard`);
  }

  function onSkip() {
    if (!validProjectId) return;
    localStorage.setItem(setupSkippedKey(validProjectId), '1');
    goDashboard();
  }

  function addComponentRow() {
    setComponents((prev) => [...prev, { name: '', description: '' }]);
  }

  function removeComponentRow(idx: number) {
    setComponents((prev) => {
      const next = prev.filter((_, i) => i !== idx);
      return next.length ? next : [{ name: '', description: '' }];
    });
  }

  function applyBulkAdd() {
    const lines = bulkText
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean);
    if (!lines.length) return;
    setComponents((prev) => {
      const existingNames = new Set(prev.map((c) => normalize(c.name).toLowerCase()).filter(Boolean));
      const additions: ComponentDraft[] = [];
      for (const name of lines) {
        const key = name.toLowerCase();
        if (existingNames.has(key)) continue;
        existingNames.add(key);
        additions.push({ name, description: '' });
      }
      const cleanedPrev = prev.filter((c) => normalize(c.name) || normalize(c.description));
      const base = cleanedPrev.length ? cleanedPrev : [];
      return [...base, ...additions, ...(base.length || additions.length ? [] : [{ name: '', description: '' }])];
    });
    setBulkText('');
  }

  async function onFinish() {
    if (!validProjectId) return;
    setSaving(true);
    setError(null);
    try {
      const trimmedProfile: ProjectProfile = {
        intended_use: normalize(profile.intended_use),
        device_description: normalize(profile.device_description),
        user_population: normalize(profile.user_population),
        use_environment: normalize(profile.use_environment),
        key_safety_characteristics: Array.isArray(profile.key_safety_characteristics)
          ? profile.key_safety_characteristics
              .map((x) => String(x).trim())
              .filter(Boolean)
          : [],
      };

      const trimmedComponents = components
        .map((c) => ({
          id: c.id,
          name: normalize(c.name),
          description: normalize(c.description) || null,
          parent_id: null,
          tags: null,
        }))
        .filter((c) => c.name);

      // Save profile + components first
      await projectProfileApi.upsert(validProjectId, trimmedProfile);
      await componentsApi.bulkReplace(validProjectId, trimmedComponents);

      // Ensure baseline project content exists after wizard completion:
      // - required docs exist
      // - risk items seeded (if empty)
      // - FMEA rows seeded (>= 5 per component)
      await projectInitializeApi.run(validProjectId);

      // Setup is no longer "skipped"
      localStorage.removeItem(setupSkippedKey(validProjectId));
      setFinished(true);
    } catch (e: any) {
      const msg = String(e?.message || 'Failed to finish setup. Please try again.');
      setError(msg);
      if (msg.toLowerCase().includes('project not found')) {
        try {
          clearCurrentProject();
        } catch {
          // ignore
        }
        navigate('/projects', { replace: true });
      }
    } finally {
      setSaving(false);
    }
  }

  async function onGenerateInitialDrafts() {
    if (!validProjectId) return;
    setGeneratingDrafts(true);
    setError(null);
    try {
      await projectInitializeFromProfileApi.run(validProjectId);
      goDashboard();
    } catch (e: any) {
      setError(e?.message || 'Failed to generate initial drafts. Please try again.');
    } finally {
      setGeneratingDrafts(false);
    }
  }

  if (!validProjectId) {
    return (
      <div className="p-6">
        <div className="mx-auto max-w-3xl rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          Missing project id.
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Project Setup Wizard</h1>
            <p className="text-sm text-gray-600">
              Add device context + components so Hazard Analysis and FMEA can be prefilled.
            </p>
          </div>
          <button
            type="button"
            onClick={onSkip}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
          >
            Skip for now
          </button>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className={`rounded-full px-3 py-1 ${step === 1 ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
              1) Device Basics
            </span>
            <span className={`rounded-full px-3 py-1 ${step === 2 ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
              2) Components
            </span>
            <span className={`rounded-full px-3 py-1 ${step === 3 ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
              3) Review
            </span>
          </div>
        </div>

        {error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">{error}</div>
        ) : null}

        {loading ? (
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <div className="flex items-center gap-3 text-gray-700">
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-gray-700" />
              Loading setup…
            </div>
          </div>
        ) : (
          <>
            {finished ? (
              <div className="rounded-lg border border-gray-200 bg-white p-6 space-y-4">
                <div className="text-lg font-semibold text-gray-900">Setup saved</div>
                <div className="text-sm text-gray-700">
                  You can optionally generate initial document drafts now. This is a deterministic draft generator (no AI) and will
                  <b> not overwrite</b> existing user-edited document content.
                </div>

                <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                  Draft generation is <b>not</b> automatic. Click the button below to generate initial drafts.
                </div>

                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
                  <button
                    type="button"
                    onClick={goDashboard}
                    className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    Skip for now
                  </button>
                  <button
                    type="button"
                    onClick={onGenerateInitialDrafts}
                    disabled={generatingDrafts}
                    className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
                  >
                    {generatingDrafts ? 'Generating drafts…' : 'Generate Initial Document Drafts'}
                  </button>
                </div>
              </div>
            ) : (
              <>
            {step === 1 ? (
              <div className="rounded-lg border border-gray-200 bg-white p-6 space-y-4">
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Intended use</label>
                    <textarea
                      className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                      rows={3}
                      value={profile.intended_use || ''}
                      onChange={(e) => setProfile((p) => ({ ...p, intended_use: e.target.value }))}
                      placeholder="e.g., Used to monitor patient vitals during clinical care"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Device description</label>
                    <textarea
                      className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                      rows={3}
                      value={profile.device_description || ''}
                      onChange={(e) => setProfile((p) => ({ ...p, device_description: e.target.value }))}
                      placeholder="Short description of the device/system"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">User population</label>
                    <input
                      className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                      value={profile.user_population || ''}
                      onChange={(e) => setProfile((p) => ({ ...p, user_population: e.target.value }))}
                      placeholder="e.g., clinicians, patients, technicians"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Use environment</label>
                    <input
                      className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                      value={profile.use_environment || ''}
                      onChange={(e) => setProfile((p) => ({ ...p, use_environment: e.target.value }))}
                      placeholder="e.g., hospital, home, lab, field"
                    />
                  </div>
                </div>

                <div className="rounded-md border border-blue-200 bg-blue-50 p-3 text-sm text-blue-900">
                  Tip: even partial info helps generate better starter hazards later.
                </div>
              </div>
            ) : null}

            {step === 2 ? (
              <div className="rounded-lg border border-gray-200 bg-white p-6 space-y-5">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="text-sm font-semibold text-gray-900">Components</div>
                    <div className="text-sm text-gray-600">Add the system components you want to analyze.</div>
                  </div>
                  <button
                    type="button"
                    onClick={addComponentRow}
                    className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
                  >
                    + Add component
                  </button>
                </div>

                <div className="rounded-md border border-gray-200 bg-gray-50 p-4 space-y-3">
                  <div className="text-sm font-semibold text-gray-900">Bulk add</div>
                  <div className="text-sm text-gray-600">Paste one component name per line.</div>
                  <textarea
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-mono"
                    rows={4}
                    value={bulkText}
                    onChange={(e) => setBulkText(e.target.value)}
                    placeholder={'Power Supply\nSensor Module\nEnclosure'}
                  />
                  <div className="flex justify-end">
                    <button
                      type="button"
                      onClick={applyBulkAdd}
                      disabled={!bulkText.trim()}
                      className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                    >
                      Add lines
                    </button>
                  </div>
                </div>

                <div className="space-y-3">
                  {components.map((c, idx) => (
                    <div key={idx} className="rounded-md border border-gray-200 p-4">
                      <div className="grid grid-cols-1 gap-3 md:grid-cols-5 md:items-start">
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700">Name</label>
                          <input
                            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                            value={c.name}
                            onChange={(e) =>
                              setComponents((prev) =>
                                prev.map((x, i) => (i === idx ? { ...x, name: e.target.value } : x))
                              )
                            }
                            placeholder="Component name"
                          />
                        </div>
                        <div className="md:col-span-3">
                          <label className="block text-sm font-medium text-gray-700">Description (optional)</label>
                          <input
                            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                            value={c.description || ''}
                            onChange={(e) =>
                              setComponents((prev) =>
                                prev.map((x, i) => (i === idx ? { ...x, description: e.target.value } : x))
                              )
                            }
                            placeholder="Short description"
                          />
                        </div>
                      </div>
                      <div className="mt-3 flex justify-end">
                        <button
                          type="button"
                          onClick={() => removeComponentRow(idx)}
                          className="text-sm text-red-600 hover:text-red-700"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {componentCount === 0 ? (
                  <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                    No components added yet. You can still finish setup, but Hazard Analysis/FMEA prefill will be limited.
                  </div>
                ) : null}
              </div>
            ) : null}

            {step === 3 ? (
              <div className="rounded-lg border border-gray-200 bg-white p-6 space-y-4">
                <div className="text-lg font-semibold text-gray-900">Review</div>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="rounded-md border border-gray-200 p-4">
                    <div className="text-sm font-semibold text-gray-900">Device Basics</div>
                    <dl className="mt-2 space-y-2 text-sm text-gray-700">
                      <div>
                        <dt className="font-medium text-gray-600">Intended use</dt>
                        <dd className="mt-1 whitespace-pre-wrap">{normalize(profile.intended_use) || '—'}</dd>
                      </div>
                      <div>
                        <dt className="font-medium text-gray-600">Device description</dt>
                        <dd className="mt-1 whitespace-pre-wrap">{normalize(profile.device_description) || '—'}</dd>
                      </div>
                      <div>
                        <dt className="font-medium text-gray-600">User population</dt>
                        <dd className="mt-1">{normalize(profile.user_population) || '—'}</dd>
                      </div>
                      <div>
                        <dt className="font-medium text-gray-600">Use environment</dt>
                        <dd className="mt-1">{normalize(profile.use_environment) || '—'}</dd>
                      </div>
                    </dl>
                    {!isProfileFilled(profile) ? (
                      <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-2 text-xs text-amber-900">
                        Device basics are empty. You can still finish, but hazard prefill may be generic.
                      </div>
                    ) : null}
                  </div>

                  <div className="rounded-md border border-gray-200 p-4">
                    <div className="text-sm font-semibold text-gray-900">Components</div>
                    <div className="mt-2 text-sm text-gray-700">{componentCount} component(s)</div>
                    <ul className="mt-2 list-disc pl-5 text-sm text-gray-700 space-y-1">
                      {components
                        .filter((c) => normalize(c.name))
                        .slice(0, 10)
                        .map((c, idx) => (
                          <li key={idx}>
                            <span className="font-medium">{normalize(c.name)}</span>
                            {normalize(c.description) ? <span className="text-gray-600"> — {normalize(c.description)}</span> : null}
                          </li>
                        ))}
                    </ul>
                    {componentCount > 10 ? (
                      <div className="mt-2 text-xs text-gray-500">…and {componentCount - 10} more</div>
                    ) : null}
                  </div>
                </div>

                <div className="rounded-md border border-blue-200 bg-blue-50 p-3 text-sm text-blue-900">
                  On finish, we’ll save profile + components. Draft document generation is optional and requires an explicit action.
                </div>
              </div>
            ) : null}

            <div className="flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setStep((s) => (s > 1 ? ((s - 1) as WizardStep) : s))}
                  disabled={step === 1 || saving}
                  className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Back
                </button>
              </div>
              <div className="flex items-center gap-2 justify-end">
                {step < 3 ? (
                  <button
                    type="button"
                    onClick={() => setStep((s) => ((s + 1) as WizardStep))}
                    disabled={!canContinue || saving}
                    className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
                  >
                    Continue
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={onFinish}
                    disabled={saving}
                    className="rounded-md bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 disabled:opacity-50"
                  >
                    {saving ? 'Finishing…' : 'Finish Setup'}
                  </button>
                )}
              </div>
            </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

